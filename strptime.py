# Formatting time_str to time object

from datetime import datetime

date_time_str = "2021-01-08T15:48:06.879811"

date_time_obj = datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%S.%f")

print(date_time_obj)
