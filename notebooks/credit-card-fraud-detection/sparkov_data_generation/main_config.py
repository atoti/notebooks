import json


class MainConfig:
    def __init__(self, main):
        self.config = self.all_profiles_dicts(main)

    # convert type to a tuple
    def convert_config_type(self, x):
        if type(x) is dict:
            minval = float(x["min"])
            maxval = float(x["max"])
            if maxval < 0:
                return (minval, float("inf"))
            else:
                return (minval, maxval)
        else:
            return x

    def all_profiles_dicts(self, main):

        main_config = json.loads(
            json.dumps(main)
            .replace("\\n", "")
            .replace("\\t", "")
            .replace("\\", "")
            .replace('"{', "{")
            .replace('}"', "}")
        )

        all_profiles = {}
        for pf in main_config:
            if pf != "leftovers.json":
                all_profiles[pf] = {}
                for qual in main_config[pf]:
                    all_profiles[pf][qual] = self.convert_config_type(
                        main_config[pf][qual]
                    )

        return all_profiles

    def in_profile(self, person_dict, profile_quals):
        for pq in profile_quals:
            if pq == "age":
                if self.fits_qual(return_age(person_dict), profile_quals[pq]) == False:
                    return False
            else:
                if self.fits_qual(person_dict[pq], profile_quals[pq]) == False:
                    return False
        return True

    def fits_qual(self, person_val, range_tuple):
        if type(range_tuple) is list:
            # matching value in string list
            # (e.g. ['M','F'])
            if unicode(person_val) in range_tuple or str(person_val) in range_tuple:
                return True
            # doesn't match
            else:
                return False

        elif type(range_tuple) is unicode or type(range_tuple) is str:
            if unicode(person_val) == unicode(range_tuple):
                return True
            # doesn't match
            else:
                return False

        # range
        if float(person_val) >= float(range_tuple[0]) and float(person_val) <= float(
            range_tuple[1]
        ):
            return True
        else:
            return False
