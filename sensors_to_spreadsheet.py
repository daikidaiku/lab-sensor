from DHT11 import GetDHT11Data
from openweather import GetOpenWeatherData
from datetime import datetime, timedelta
import os
import csv
import configparser
import pandas as pd
import requests
import logging
import subprocess
import os
from dotenv import load_dotenv

# # .envファイルの読み込み
load_dotenv()

#グローバル変数
global masterdate

######DHT11のデータ取得######
def getdata_DHT11(device):
    #値が得られないとき、最大device.Retry回スキャンを繰り返す
    for i in range(device.Retry):
        #スキャンしてセンサ値取得
        try:
            sensorValue = GetDHT11Data().get_sensor_data()
        #エラーが出たらログ出力
        except:
            logging.warning(f'retry to get data [loop{str(i)}, date{str(masterdate)}, device{device.DeviceName}, sensor]')
            sensorValue = None
            continue
        else:
            break
    #値取得できていたら、POSTするデータをdictに格納
    if sensorValue is not None:
        #POSTするデータ
        data = {        
            'DeviceName': device.DeviceName,
            'Date_Master': str(masterdate),
            'Date': str(datetime.today()),
            'Temperature': str(sensorValue['Temperature']),
            'Humidity': str(sensorValue['Humidity']),
            'THI': str(sensorValue['THI'])
        }
        return data
    #取得できていなかったら、ログ出力
    else:
        logging.error(f'cannot get data [loop{str(device.Retry)}, date{str(masterdate)}, device{device.DeviceName}, timeout{device.Timeout}]')
        return None

######OpenWeatherのデータ取得######
def getdata_OpenWeather(device):
    #値が得られないとき、最大device.Retry回スキャンを繰り返す
    for i in range(device.Retry):
        #スキャンしてセンサ値取得
        try:
            sensorValue = GetOpenWeatherData().get_sensor_data()
        #エラーが出たらログ出力
        except:
            logging.warning(f'retry to get data [loop{str(i)}, date{str(masterdate)}, device{device.DeviceName}, sensor]')
            sensorValue = None
            continue
        else:
          break
    #値取得できていたら、POSTするデータをdictに格納
    if sensorValue is not None:
        #POSTするデータ
        data = {        
            'DeviceName': device.DeviceName,
            'Date_Master': str(masterdate),
            'Date': str(datetime.today()),
            'Temperature': str(sensorValue['Temperature']),
            'Humidity': str(sensorValue['Humidity']),
            'Pressure': str(sensorValue['Pressure']),
            'THI': str(sensorValue['THI'])
        }
        return data
    #取得できていなかったら、ログ出力してBluetoothアダプタ再起動
    else:
        logging.error(f'cannot get data [loop{str(device.Retry)}, date{str(masterdate)}, device{device.DeviceName}, timeout{device.Timeout}]')
        return None

######データのCSV出力######
def output_csv(data, csvpath):
    dvname = data['DeviceName']
    monthstr = masterdate.strftime('%Y%m')
    #出力先フォルダ名
    outdir = f'{csvpath}/{dvname}/{masterdate.year}'
    #出力先フォルダが存在しないとき、新規作成
    os.makedirs(outdir, exist_ok=True)
    #出力ファイルのパス
    outpath = f'{outdir}/{dvname}_{monthstr}.csv'
    
    #出力ファイル存在しないとき、新たに作成
    if not os.path.exists(outpath):        
        with open(outpath, 'w', newline="") as f:
            writer = csv.DictWriter(f, data.keys())
            writer.writeheader()
            writer.writerow(data)
    #出力ファイル存在するとき、1行追加
    else:
        with open(outpath, 'a', newline="") as f:
            writer = csv.DictWriter(f, data.keys())
            writer.writerow(data)

######Googleスプレッドシートにアップロードする処理######
def output_spreadsheet(all_values_dict):
    #APIのURL
    url = os.getenv('SPREADSHEET_API_KEY')
    #APIにデータをPOST
    response = requests.post(url, json=all_values_dict)
    print(response.text)
    
    
######メイン######
if __name__ == '__main__':    
    #開始時刻を取得
    startdate = datetime.today()
    #開始時刻を分単位で丸める
    masterdate = startdate.replace(second=0, microsecond=0)   
    if startdate.second >= 30:
        masterdate += timedelta(minutes=1)
    
    #設定ファイルとデバイスリスト読込
    cfg = configparser.ConfigParser()
    cfg.read('./config.ini', encoding='utf-8')
    df_devicelist = pd.read_csv('./DeviceList.csv')
    #全センサ数とデータ取得成功数
    sensor_num = len(df_devicelist)
    success_num = 0
    
    #ログの初期化
    logname = f"/sensorlog_{str(masterdate.strftime('%y%m%d'))}.log"
    logging.basicConfig(filename=cfg['Path']['LogOutput'] + logname, level=logging.INFO)
    
    #取得した全データ保持用dict
    all_values_dict = None
    
    ######デバイスごとにデータ取得######
    for device in df_devicelist.itertuples():
        #DHT11
        if device.SensorType == 'DHT11':
            data = getdata_DHT11(device)
        #API
        elif device.SensorType == 'API':
            data = getdata_OpenWeather(device)
        #上記以外
        else:
            data = None

        #データが存在するとき、全データ保持用Dictに追加し、CSV出力
        if data is not None:
            #all_values_dictがNoneのとき、新たに辞書を作成
            if all_values_dict is None:
                all_values_dict = {data['DeviceName']: data}
            #all_values_dictがNoneでないとき、既存の辞書に追加
            else:
                all_values_dict[data['DeviceName']] = data

            #CSV出力
            output_csv(data, cfg['Path']['CSVOutput'])
            #成功数プラス
            success_num+=1


######Googleスプレッドシートにアップロードする処理######
    output_spreadsheet(all_values_dict)

    #処理終了をログ出力
    logging.info(f'[masterdate{str(masterdate)} startdate{str(startdate)} enddate{str(datetime.today())} success{str(success_num)}/{str(sensor_num)}]')