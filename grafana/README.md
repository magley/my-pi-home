# Installing

Download grafana.
IN /bin, run grafana-server.
Open localhost:3000; login is (admin, admin).
Click on add data source.
Find InfluxDB.
Follow instructions from the presentation for setting up InfluxDB.
Then you can create dashboards or import them. When you change stuff, save it and export it to .json and put it in this folder.

# Embedding

To enable iframe embedding, you have to change the conf/defaults.ini file:

1) To allow embedding, change this:
```
allow_embedding = true
```

2) To allow embedding without the need for login, change this:
```
[auth.anonymous]
enabled = true
```