import sys
import json
import collections
import math

from sklearn import linear_model

ratings = {
    'Generic': 0,
    'Poor (P)': 10,
    'Fair (F)': 20,
    'Good (G)': 30,
    'Good Plus (G+)': 40,
    'Very Good (VG)': 50,
    'Very Good Plus (VG+)': 60,
    'Near Mint (NM or M-)': 70,
    'Mint (M)': 80,
}

sum_ = 0
with open(sys.argv[1]) as infile:
    for line in infile:
        data = json.loads(line)
        # print(f'{data["n_for_sale"]}\t{len(data["records_for_sale"])}\t{data["release_id"]}')
        grouped = collections.defaultdict(list)
        x = []
        y = []
        for s in data["records_for_sale"]:
            key = (s["media_condition"], s["sleeve_condition"])
            sc = s["sleeve_condition"]
            if sc is None or sc == "No Cover":
                sc = "Generic"
            # print(ratings[s["media_condition"]])
            # print(ratings[sc])
            x.append([ratings[s["media_condition"]], ratings[sc]])
            y.append(math.log(s["price_info"]["price_dollars"]))
            # print(s["sleeve_condition"])
            grouped[key].append(s["price_info"]["price_dollars"])
        # print(grouped)
        # print()

        
        # x = list(zip(*x))
        model = linear_model.LinearRegression()
        try:
            model.fit(x, y)
        except ValueError:
            pass
        else:
            predicted = model.predict([[50, 50]])
            # rfs = data.pop("records_for_sale")
            # stats = data.pop("statistics")
            # stats.pop('Avg Rating')
            # conds = [ratings[d["media_condition"]] for d in rfs]
            # prices = [d["price_info"]["price_dollars"] for d in rfs]
            # print(data['release_id'])
            # print(stats)
            # print(conds)
            # print(prices)
            # print(x)
            # print(int(math.exp(predicted[0]) / 5) * 5)
            print(math.exp(predicted[0]))
            sum_ += math.exp(predicted[0])
            # print(math.exp(predicted[0]) / 5) * 5)
            # print()

print(sum_ * 0.80)
