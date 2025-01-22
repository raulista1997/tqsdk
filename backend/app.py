from flask import Flask, send_from_directory
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from tqsdk import TqApi, TqAuth, TqBacktest, TqSim, TqKq, TargetPosTask, BacktestFinished
from datetime import date, datetime
import logging
import pytz
import math
from contextlib import closing
import os
import signal

app = Flask(__name__, static_folder="static")
CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = Flask(__name__, static_folder="static")


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


@app.route('/execute', methods=['POST'])
def execute_strategy():
    # Get JSON data from the request
    data = request.json
    logging.info(f"Received request data: {data}")

    try:
        # Extract parameters
        mode = int(data.get("mode"))
        username = data.get("username")
        password = data.get("password")
        trade_symbol1 = data.get("trade_symbol1")
        trade_symbol2 = data.get("trade_symbol2")
        track_symbol = data.get("track_symbol")
        position_percent1 = float(data.get("position_percent1", 0))
        position_percent2 = float(data.get("position_percent2", 0))
        track_symbol_buy_low1 = float(data.get("track_symbol_buy_low1", 0))
        track_symbol_buy_high1 = float(data.get("track_symbol_buy_high1", 0))
        track_symbol_buy_low2 = float(data.get("track_symbol_buy_low2", 0))
        track_symbol_buy_high2 = float(data.get("track_symbol_buy_high2", 0))
        sell_at_profit_high1 = float(data.get("sell_at_profit_high1", 0))
        sell_at_profit_low1 = float(data.get("sell_at_profit_low1", 0))
        sell_at_profit_high2 = float(data.get("sell_at_profit_high2", 0))
        sell_at_profit_low2 = float(data.get("sell_at_profit_low2", 0))
        sell_at_loss_morning = float(data.get("sell_at_loss_morning", 0))
        sell_at_loss_afternoon = float(data.get("sell_at_loss_afternoon", 0))
        track_symmbol_add_buy = float(data.get("track_symmbol_add_buy", 0))
        additional_position_percent = float(
            data.get("additional_position_percent", 0.1)
        )

        # Mode 2 specific fields
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        # Validate required fields
        if mode not in [1, 2]:
            return jsonify({"error": "Invalid mode. Must be 1 or 2."}), 400

        if not username or not password:
            return jsonify({"error": "Username and password are required."}), 400

        if mode == 2 and (not start_date or not end_date):
            return jsonify({"error": "Start date and end date are required for mode 2."}), 400

        if not all([trade_symbol1, trade_symbol2, track_symbol, position_percent1, position_percent2]):
            return jsonify({"error": "Missing required parameters."}), 400

        # Convert start_date and end_date to date objects if provided
        start_dt = date.fromisoformat(start_date) if start_date else None
        end_dt = date.fromisoformat(end_date) if end_date else None

        # Run the strategy
        def semi_auto_strategy_short_term():
            logging.info(f"Starting strategy with mode={mode}")

            if mode == 1:
                logging.info("Running in mode 1 (simulation).")
                api = TqApi(TqKq(), auth=TqAuth(
                    username, password), web_gui=":80")
            else:
                logging.info("Running in mode 2 (backtest).")
                api = TqApi(
                    TqSim(),
                    auth=TqAuth(username, password),
                    backtest=TqBacktest(start_dt=start_dt, end_dt=end_dt),
                    web_gui=":80"
                )
                acc = TqSim()

            try:
                logger.info("Login successful")
                account = api.get_account()  # 获取账户信息引用
                logger.info(f"Account balance: {account.balance}")

                # 合约市价
                quote1 = api.get_quote(trade_symbol1)
                logger.info(f"Initial price for {trade_symbol1}: {quote1}")
                quote2 = api.get_quote(trade_symbol2)
                logger.info(f"Initial price for {trade_symbol2}: {quote2}")

                # 现有合约持仓
                position1 = api.get_position(trade_symbol1)
                logger.info(
                    f"Initial position for {trade_symbol1}: {position1}")
                position2 = api.get_position(trade_symbol2)
                logger.info(
                    f"Initial position for {trade_symbol2}: {position2}")

                # 上证指数
                quote_shangzheng = api.get_quote(track_symbol)
                logger.info(
                    f"Index point for {track_symbol}: {quote_shangzheng}")

                # Define the China timezone
                china_tz = pytz.timezone('Asia/Shanghai')
                today = datetime.now(china_tz).date()
                nine_thirty = china_tz.localize(
                    datetime(today.year, today.month, today.day, 9, 30))
                ten_thirty = china_tz.localize(
                    datetime(today.year, today.month, today.day, 10, 30))
                eleven_thirty = china_tz.localize(
                    datetime(today.year, today.month, today.day, 11, 30))
                one_clock = china_tz.localize(
                    datetime(today.year, today.month, today.day, 13, 0))
                two_clock = china_tz.localize(
                    datetime(today.year, today.month, today.day, 14, 0))
                three_clock = china_tz.localize(
                    datetime(today.year, today.month, today.day, 15, 0))

                # 保证金比例
                ratio = 0.12
                # trade symbol 1
                symbol_margin = quote1.last_price * quote1.volume_multiple * ratio
                logger.info(
                    f"Total position for {trade_symbol1}: {api.get_position(trade_symbol1).pos_long_today}")
                num = math.ceil(account.balance *
                                position_percent1 / symbol_margin)

                # trade symbol 2
                symbol_margin2 = quote2.last_price * quote2.volume_multiple * ratio
                num2 = int(account.balance *
                           position_percent2 / symbol_margin2)

                buy_position1 = math.ceil(num / 2)
                sell_position1 = round(position1.pos_long / 2, 0)
                buy_position2 = math.ceil(num2 / 2)
                sell_position2 = round(position2.pos_long / 2, 0)

                if additional_position_percent > 0:
                    additional_num = math.ceil(
                        account.balance * additional_position_percent / symbol_margin)
                    additional_buy_position = math.ceil(additional_num)
                    additional_sell_position = round(position1.pos_long, 0)

                logger.info(
                    f"Current buy position: {buy_position1}, sell position: {sell_position1}")

                # 设置分批买入价格
                # 点位区间1
                # 在点位区间分两次买入，第一次是达到买入点位上线以内，第二次是达到点位区间中值
                buy_price_diff1 = track_symbol_buy_high1 - track_symbol_buy_low1
                buy_price_1_1 = track_symbol_buy_high1
                buy_price_1_2 = buy_price_1_1 - buy_price_diff1 / 2
                # 在点位区间分两次卖出，第一次是达到卖出上线+1，第二次是达到点位区间中值
                sell_price_diff1 = sell_at_profit_high1 - sell_at_profit_low1
                sell_price_1_1 = sell_at_profit_low1 + 1
                sell_price_1_2 = sell_price_1_1 + sell_price_diff1 / 2
                # 点位区间2
                buy_price_diff2 = track_symbol_buy_high2 - track_symbol_buy_low2
                buy_price_2_1 = track_symbol_buy_high2
                buy_price_2_2 = buy_price_2_1 - buy_price_diff2 / 2
                # 在点位区间分两次卖出，第一次是达到卖出上线+1，第二次是达到点位区间中值
                sell_price_diff1 = sell_at_profit_high1 - sell_at_profit_low1
                sell_price_2_1 = sell_at_profit_low1 + 1
                sell_price_2_2 = sell_price_2_1 + sell_price_diff1 / 2
                # 用实盘账户来交易（如中信建投）
                # api = TqApi(TqAccount("Z中信建投", "320102", "123456"),
                # auth = TqAuth("快期账户", "账户密码"))
                klines = api.get_kline_serial(
                    track_symbol, 5*60, data_length=15)
                # kline for trade symbol 1
                klines_target1 = api.get_kline_serial(
                    trade_symbol1, 5*60, data_length=15)
                position1 = api.get_position(trade_symbol1)
                target_pos1 = TargetPosTask(api, trade_symbol1)
                # kline for trade symbol 2
                klines_target2 = api.get_kline_serial(
                    trade_symbol2, 5*60, data_length=15)
                position2 = api.get_position(trade_symbol2)
                target_pos2 = TargetPosTask(api, trade_symbol2)

                # Further calculations (omitting unchanged logic for brevity)
                with closing(api):
                    while True:
                        api.wait_update()
                        current_time = datetime.now(china_tz)
                        logger.info(f"Current time in China: {current_time}")

                        if api.is_changing(klines):
                            logger.info(
                                f"Current buy position: {buy_position1}")
                            ma = sum(klines_target1.close.iloc[-15:]) / 15
                            ma2 = sum(klines_target2.close.iloc[-15:]) / 15
                            ma_track = sum(klines.close.iloc[-15:]) / 15
                            logger.info(
                                f"Latest price for {trade_symbol1}: {quote1.last_price}, MA: {ma}")
                            logger.info(
                                f"Latest price for {trade_symbol2}: {quote2.last_price}, MA: {ma2}")
                            logger.info(
                                f"Latest index point for {track_symbol}: {klines.close.iloc[-1]}, MA: {ma_track}")

                            # 开多单情况 - 如果上证指数在某个价格区间
                            # if track_symbol_buy_low1 <= klines.close.iloc[-1] < track_symbol_buy_high1:
                            if klines.close.iloc[-1] <= buy_price_1_1:
                                # target_pos.set_target_volume(buy_position*4)
                                target_pos1.set_target_volume(buy_position1)
                                logger.info(
                                    f"第一批多单 {buy_position1} 手 for {trade_symbol1} last price = {quote1.last_price}")
                                target_pos2.set_target_volume(buy_position2)
                                logger.info(
                                    f"第一批多单 {buy_position2} 手 for {trade_symbol2} last price = {quote2.last_price}")
                            if klines.close.iloc[-1] <= buy_price_1_2:
                                # target_pos.set_target_volume(buy_position*4)
                                target_pos1.set_target_volume(buy_position1*2)
                                logger.info(
                                    f"第二批多单 {buy_position1} 手 for {trade_symbol1} last price = {quote1.last_price}")
                                target_pos2.set_target_volume(buy_position2*2)
                                logger.info(
                                    f"第二批多单 {buy_position2} 手 for {trade_symbol2} last price = {quote2.last_price}")
                            # if track_symbol_buy_low2 <= klines.close.iloc[-1] < track_symbol_buy_high2:
                                # target_pos.set_target_volume(buy_position*4)
                            #    target_pos1.set_target_volume(buy_position1)
                                # target_pos2.set_target_volume(buy_position2)

                            # 追多仓条件, 在10:30 - 11:30 或 14:00 - 15:00 之间， 如果总分仓位小于20%，并且点数突破
                            if (ten_thirty <= current_time <= eleven_thirty) or (two_clock <= current_time <= three_clock):
                                current_total_position_ = api.get_position(
                                    trade_symbol1).pos_long_today + api.get_position(trade_symbol2).pos_long_today
                                # 修改价格比例，增加突破9:30 - 11:30之间的高点或13:00 - 14:00之间的高点, 如果只占不满20%仓位，即加仓
                                if (klines.close.iloc[-1] > track_symmbol_add_buy or klines.close.iloc[-1] > max(klines.close)) and current_total_position_ < 0.2 * account.balance:
                                    # target_pos.set_target_volume(buy_position*4)
                                    target_pos1.set_target_volume(
                                        additional_buy_position)
                                    logger.info(
                                        f"追加多单 {additional_buy_position} 手 for {trade_symbol1} last price = {quote1.last_price}")
                                    target_pos2.set_target_volume(
                                        additional_buy_position)
                                    logger.info(
                                        f"追加多单 {additional_buy_position} 手 for {trade_symbol2} last price = {quote2.last_price}")
                            # 上午高抛区间1
                            # if nine_thirty <= current_time <= eleven_thirty:
                            # if sell_at_profit_low1 < klines.close.iloc[-1] <= sell_at_profit_high1:
                            if klines.close.iloc[-1] >= sell_price_1_1:
                                # target_pos.set_target_volume(buy_position*4)
                                target_pos1.set_target_volume(sell_position1)
                                logger.info(
                                    f"第一批卖出多单 {sell_position1} 手 for {trade_symbol1} last price = {quote1.last_price}")
                                target_pos2.set_target_volume(sell_position2)
                                logger.info(
                                    f"第一批卖出多单 {sell_position2} 手 for {trade_symbol2} last price = {quote2.last_price}")
                            if klines.close.iloc[-1] >= sell_price_1_2:
                                # target_pos.set_target_volume(buy_position*4)
                                target_pos1.set_target_volume(sell_position1)
                                logger.info(
                                    f"第二批卖出多单 {sell_position1} 手 for {trade_symbol1} last price = {quote1.last_price}")
                                target_pos2.set_target_volume(sell_position2)
                                logger.info(
                                    f"第二批卖出多单 {sell_position2} 手 for {trade_symbol2} last price = {quote2.last_price}")
                            # 高抛区间2
                            # if sell_at_profit_low2 < klines.close.iloc[-1] <= sell_at_profit_high2:
                            if klines.close.iloc[-1] >= sell_price_2_1:
                                # target_pos.set_target_volume(buy_position*4)
                                target_pos1.set_target_volume(0)
                                logger.info(
                                    f"清空多单 {sell_position1} 手 for {trade_symbol1} last price = {quote1.last_price}")
                                target_pos2.set_target_volume(0)
                                logger.info(
                                    f"清空多单 {sell_position2} 手 for {trade_symbol2} last price = {quote2.last_price}")
                            # 上午跌破止损条件 - 跌破3100点或者9:30 - 11:30之间低点-5
                            if ten_thirty <= current_time <= eleven_thirty:
                                if klines.close.iloc[-1] < sell_at_loss_morning or klines.close.iloc[-1] < min(klines.close)-5:
                                    # target_pos.set_target_volume(buy_position*4)
                                    target_pos1.set_target_volume(0)
                                    logger.info(
                                        f"止损多单 {position1} 手 for {trade_symbol1} last price = {quote1.last_price}")
                                    target_pos2.set_target_volume(0)
                                    logger.info(
                                        f"止损多单 {position2} 手 for {trade_symbol2} last price = {quote2.last_price}")
                            # 下午跌破止损条件
                            if two_clock <= current_time <= three_clock:
                                if klines.close.iloc[-1] < sell_at_loss_afternoon or klines.close.iloc[-1] < min(klines.close)-5:
                                    # target_pos.set_target_volume(buy_position*4)
                                    target_pos1.set_target_volume(0)
                                    logger.info(
                                        f"止损多单 {position1} 手 for {trade_symbol1} last price = {quote1.last_price}")
                                    target_pos2.set_target_volume(0)
                                    logger.info(
                                        f"止损多单 {position2} 手 for {trade_symbol2} last price = {quote2.last_price}")
                        else:
                            logger.info(f"价格没有变化")
                        logger.info(f"one round simple logic finished")
                    if mode == 2:
                        logger.info("Backtest completed successfully.")
                        return "Backtest finished."
                    else:
                        return "Simulation finished."

            except BacktestFinished as e:
                logger.info("Backtest completed successfully.")
                logger.info(acc.trade_log)

        result = semi_auto_strategy_short_term()
        return jsonify(result)

    except Exception as e:
        logging.error(f"Error executing strategy: {e}")
        return jsonify({"error": str(e)}), 500

# stop the strategy


@app.route('/stop', methods=['POST'])
def stop_strategy():
    # Logic to stop the app
    os.kill(os.getpid(), signal.SIGINT)  # Simulate Ctrl+C
    return jsonify({"message": "Strategy stopped successfully"}), 200


if __name__ == "__main__":
    # Default to port 8000 if PORT is not set
    app.run(host="0.0.0.0", port=5001)
