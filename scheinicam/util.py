import datetime

def time_dict_to_time(time_dict):
    return datetime.time(time_dict["hour"], time_dict["minute"], time_dict["second"])