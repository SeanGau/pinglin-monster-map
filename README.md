# 坪林巡怪地圖

上線版本及計畫詳細內容： https://strangepinglin.collective.tw/

程式碼基底為 SeanGau 的 [大河小溪全民齊督工](https://github.com/SeanGau/river-watcher)

- database: postgreSQL + postgis
- Backend: Flask(python)
- Frontend: jinja2, pug, sass
- extensions: leaflet

---

# How To Dev
## requirement
1. python3.6^
2. postgreSQL + postgis
## start
3. install ```python-venv``` first
4. create venv
5. 
```
pip install -r requirement.txt
```
6. rename ```config.example.py``` to ```config.py``` and fill it
7. 
```
python app.py
```
8. visit localhost:5000
