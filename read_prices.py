import statistics
import csv
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
typical_ratios = {
    'Generic': 0.3511,
    'Poor (P)': 0.3538,
    'Fair (F)': 0.3538,
    'Good (G)': 0.3582,
    'Good Plus (G+)': 0.3598,
    'Very Good (VG)': 0.3813,
    'Very Good Plus (VG+)': 0.5001,
    'Near Mint (NM or M-)': 1.0000,
    'Mint (M)': 1.9135,
}

ratios = collections.defaultdict(list)
rows = []
sum_ = 0
with open(sys.argv[1]) as infile:
    for line in infile:
        data = json.loads(line)
        # print(f'{data["n_for_sale"]}\t{len(data["records_for_sale"])}\t{data["release_id"]}')
        grouped = collections.defaultdict(list)
        x = []
        y = []
        for s in data["records_for_sale"]:
            sc = s["sleeve_condition"]
            if sc is None or sc == "No Cover":
                sc = "Generic"
            key = (s["media_condition"], sc)
            # print(ratings[s["media_condition"]])
            # print(ratings[sc])
            x.append([ratings[s["media_condition"]], ratings[sc]])
            y.append(math.log(s["price_info"]["price_dollars"]))
            # print(s["sleeve_condition"])
            grouped[key].append(s["price_info"]["price_dollars"])

        above = {}
        for r in ratings:
            above[r] = []
            # print(r)
            for (mc, sc), price_list in grouped.items():
                if ratings[mc] >= ratings[r] and ratings[sc] >= ratings[r]:
                    above[r].extend(price_list)
            #         print(mc, sc, price_list)
            # print()

        lowest = {}
        for r, price_list in above.items():
            lowest[r] = min(price_list) if price_list else None
            # print(r, min(price_list) if price_list else None, list(sorted(price_list))[:5])

        if lowest['Near Mint (NM or M-)'] is not None:
            for r, mv in lowest.items():
                if mv is not None:
                    ratio = mv / lowest['Near Mint (NM or M-)']
                    ratios[r].append(ratio)

        near_mint_guesses = {}
        for r, ratio in typical_ratios.items():
            mv = lowest[r]
            if mv is not None:
                near_mint_guesses[r] = mv / ratio

        if lowest['Near Mint (NM or M-)'] is not None:
            nmv = lowest['Near Mint (NM or M-)']
        else:
            try:
                nmv = statistics.mean(near_mint_guesses.values())
            except statistics.StatisticsError:
                nmv = None

        if nmv is not None:
            for r, mv in lowest.items():
                if mv is None:
                    lowest[r] = nmv * typical_ratios[r]
                    
        row = {}
        row["release_id"] = data["release_id"]
        row["n_for_sale"] = data["n_for_sale"]
        row.update(data["statistics"])
        row.update(lowest)
        rows.append(row)
        # import pprint
        # pprint.pprint(row, sort_dicts=False)
        # print(grouped)
        # breakpoint()
        # print(grouped)
        # print()
        # import pprint
        # print(data["release_id"])
        # pprint.pprint(data["statistics"])
        # for key, price_list in sorted(grouped.items(), key=lambda i: ratings[i[0][0]] + ratings[i[0][1]], reverse=True):
        #     print(key, price_list)
        
        # x = list(zip(*x))
        # model = linear_model.LinearRegression()
        # try:
        #     model.fit(x, y)
        # except ValueError:
        #     pass
        # else:
        #     predicted = model.predict([[50, 50]])
        #     print(predicted)
        #     # rfs = data.pop("records_for_sale")
        #     # stats = data.pop("statistics")
        #     # stats.pop('Avg Rating')
        #     # conds = [ratings[d["media_condition"]] for d in rfs]
        #     # prices = [d["price_info"]["price_dollars"] for d in rfs]
        #     # print(data['release_id'])
        #     # print(stats)
        #     # print(conds)
        #     # print(prices)
        #     # print(x)
        #     # print(int(math.exp(predicted[0]) / 5) * 5)
        #     try:
        #         pred = math.exp(predicted[0])
        #     except OverflowError:
        #         pred = 0
        #     sum_ += pred
        #     print(pred)
        #     # print(math.exp(predicted[0]) / 5) * 5)
        #     # print()
        # print()
        
with open('prices.csv', 'w') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=list(row.keys()))
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

sums = dict((r, 0) for r in ratings)
for r in ratings:
    for row in rows:
        sums[r] += row[r] if row[r] is not None else 0

print(sums)
for r, ratio_list in ratios.items():
    print(r, statistics.median(ratio_list))
