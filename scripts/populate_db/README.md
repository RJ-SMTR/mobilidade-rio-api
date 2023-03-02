# Useful tips for `populate_db`

Put your tables inside fixtures folder, like in this example:

```
Folder structure            table in database
-----------------------     -----------------
- 📂fixtures
  - 📂pontos
    - 🗒️stops.txt           pontos_stops
    - 🗒️shapes.txt          pontos_shapes
    - 🗒️trips.txt           pontos_trips
  - 📂predictor
    - 🗒️median.txt          predictor_median
    - 🗒️prediction.txt      predictor_prediction
  - 📂feedback
    - 🗒️brt.txt             feedback_brt
```