import argparse
import json
from datetime import datetime
from getpass import getpass

import matplotlib.pyplot as plt
import requests
from requests.auth import HTTPBasicAuth


def request_data_from_server(args: argparse.Namespace):
    payload = {
        "province": args.province,
        "sample": args.sample,
        "filter_date_range": f"{args.start_date} - {args.end_date}",
    }

    basic = HTTPBasicAuth(args.user, args.password)

    print("Sending request to server...")
    r = requests.get(
        "https://sitoscope.naamii.org.np/samples/filter", params=payload, auth=basic
    )

    if r.status_code == 200:
        print(f"Successfully received server response from {r.url}")
        data = json.loads(r.text)["data"]
        return data
    else:
        print(f"Error {r.status_code} from {r.url}, {r.text}")
        raise Exception("Error when receiving server response.")


def autopct_format(values):
    def my_format(pct):
        total = sum(values)
        val = int(round(pct * total / 100.0))
        return "{v:d}".format(v=val)

    return my_format


def create_charts(args: argparse.Namespace):
    data = request_data_from_server(args)
    print(data)
    for category in data.keys():
        for region in data[category]:
            months = [
                datetime.strptime(entry["month"], "%Y-%m-%d").strftime("%b %Y")
                for entry in data[category][region]["by_month"]
            ]
            counts = [entry["count"] for entry in data[category][region]["by_month"]]

            if months:
                fig, axes = plt.subplots(
                    2, 1, figsize=(4 + len(months), 10), constrained_layout=True
                )
                bars = axes[0].bar(months, counts, color="skyblue")
                axes[0].set_title(f"{category} Samples Count by Month in {region}")
                axes[0].set_xlabel("Month")
                axes[0].set_ylabel("Count")
                axes[0].tick_params(axis="x", rotation=45)

                # Adding count labels to each bar
                for bar, count in zip(bars, counts):
                    axes[0].text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height(),
                        str(count),
                        ha="center",
                        va="bottom",
                    )

                # Plotting pie charts for total collected and remaining samples
                collected = data[category][region]["total_count"]
                if collected:
                    remaining = max(1000 - collected, 0)
                    sizes = [collected, remaining]
                    labels = ["Collected", "Remaining"]
                    colors = ["lightblue", "lightgreen"]
                    axes[1].pie(
                        sizes,
                        labels=labels,
                        autopct=autopct_format(sizes),
                        colors=colors,
                        startangle=90,
                    )
                    axes[1].set_title(f"Total {category} Samples in {region}")

                if not args.show:
                    filename = (
                        f"{category}_sample_{region}_{months[0]}_to_{months[-1]}.png"
                    )
                    plt.savefig(
                        filename,
                        dpi=300,
                        bbox_inches="tight",
                    )
                    print(f"Saved {filename}")
    if args.show:
        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create plots of sample collection statistics."
    )

    parser.add_argument(
        "-u", "--user", type=str, required=True, help="Sitoscope username"
    )
    parser.add_argument(
        "-sp",
        "--secure-password",
        action="store_true",
        dest="password",
        help="Sitoscope account password",
    )

    parser.add_argument(
        "-sd",
        "--start-date",
        type=str,
        default="2021-01-01",
        help="Filter samples starting from this date, format YYYY-MM-DD",
    )

    parser.add_argument(
        "-ed",
        "--end-date",
        type=str,
        default="2024-03-01",
        help="Filter samples upto from this date, default is today, format YYYY-MM-DD",
    )

    parser.add_argument(
        "-s",
        "--sample",
        nargs="+",
        help="Samples to filter",
        required=True,
        choices=["Water", "Vegetable", "Stool"],
        default="Stool",
    )

    parser.add_argument(
        "-p",
        "--province",
        nargs="+",
        help="Provinces to filter",
        required=True,
        choices=["P1", "MP", "BP", "LP", "GP", "KP", "SP"],
        default="P1",
    )

    parser.add_argument("--show", default=True, action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    print(args)

    if args.password:
        print(f"Password for user {args.user}")
        args.password = getpass()
    create_charts(args=args)
