import pandas as pd
import os
import argparse
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.colors import LogNorm
from itertools import combinations
from scipy.stats import ranksums


def load_and_prepare_data(file_path):
    data = pd.read_csv(file_path)
    data["Date"] = pd.to_datetime(data["Date"], format="%d.%m.%Y")
    return data


def calculate_moving_average(data, window, center=True):
    return data.rolling(window=window, center=center).mean()


def weekdays(data):
    os.makedirs("./plots/weekdays", exist_ok=True)

    daily_data = data.resample("D", on="Date").sum().reset_index()

    average_drinks_per_weekday = (
        daily_data.groupby(daily_data["Date"].dt.day_name())["Drinks"]
        .mean()
        .reindex(
            [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
        )
    )

    def bar_chart():
        plt.figure()
        plt.bar(
            average_drinks_per_weekday.index,
            average_drinks_per_weekday.values,
        )
        plt.title("Average Drinks per Weekday")
        plt.xlabel("Weekday")
        plt.ylabel("Average Drinks")
        plt.savefig("./plots/weekdays/drinks_per_weekday.png")
        plt.close()

    def boxplot():
        plt.figure()
        daily_data["Weekday"] = daily_data["Date"].dt.day_name()
        daily_data["Weekday"] = pd.Categorical(
            daily_data["Weekday"],
            categories=[
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ],
            ordered=True,
        )
        plt.boxplot(
            [
                daily_data[daily_data["Weekday"] == day]["Drinks"]
                for day in daily_data["Weekday"].cat.categories
            ],
            tick_labels=daily_data["Weekday"].cat.categories,
            vert=False,
            patch_artist=True,
        )
        plt.title("Box Plot of Drinks per Weekday")
        plt.xlabel("Drinks")
        plt.ylabel("Weekday")
        plt.savefig("./plots/weekdays/boxplot_weekday.png")
        plt.close()

    weekday_pairs = list(combinations(average_drinks_per_weekday.index, 2))
    ttest_results = pd.DataFrame(
        index=average_drinks_per_weekday.index, columns=average_drinks_per_weekday.index
    )

    def wilcoxon():
        for day1, day2 in weekday_pairs:
            drinks_day1 = daily_data[daily_data["Date"].dt.day_name() == day1]["Drinks"]
            drinks_day2 = daily_data[daily_data["Date"].dt.day_name() == day2]["Drinks"]
            stat, p_value = ranksums(drinks_day1, drinks_day2)
            ttest_results.loc[day1, day2] = p_value
            ttest_results.loc[day2, day1] = p_value

        plt.figure(figsize=(10, 8))
        sns.heatmap(
            ttest_results.astype(float),
            annot=True,
            cmap="coolwarm",
            cbar_kws={"label": "p-value"},
            norm=LogNorm(
                vmin=ttest_results.min().min(), vmax=ttest_results.max().max()
            ),
        )
        plt.title("Wilcoxon Rank-Sum Test p-values between Weekdays")
        plt.xlabel("Weekday")
        plt.ylabel("Weekday")
        plt.savefig("./plots/weekdays/wilcoxon_heatmap.png")
        plt.close()

    bar_chart()
    boxplot()
    wilcoxon()


def daily(data):
    os.makedirs("./plots/daily", exist_ok=True)

    # Aggregate daily
    daily_data = data.resample("D", on="Date").sum().reset_index()
    daily_data["Moving_Avg"] = calculate_moving_average(daily_data["Drinks"], window=7)

    def histogram():
        plt.figure()
        plt.hist(daily_data["Drinks"], edgecolor="black")
        plt.title("Histogram of Daily Drinks")
        plt.xlabel("Daily Drinks")
        plt.ylabel("Frequency")
        plt.savefig("./plots/daily/histogram_daily.png")
        plt.close()

    def cluster():
        jitter_y = np.random.normal(0, 0.1, len(daily_data))
        plt.figure()
        jitter_x = np.random.uniform(-0.25, 0.25, len(daily_data))
        plt.scatter(daily_data["Drinks"] + jitter_x, jitter_y, alpha=0.5)
        plt.title("Daily Drinks Cluster Plot")
        plt.xlabel("Daily Drinks")
        plt.yticks([])  # Remove Y-axis labels as they don't have a specific meaning
        plt.savefig("./plots/daily/cluster_plot_daily.png")
        plt.close()

    def violin():
        plt.figure()
        sns.violinplot(x=daily_data["Drinks"])
        plt.title("Daily Drinks Violin Plot")
        plt.xlabel("Daily Drinks")
        plt.savefig("./plots/daily/violin_plot_daily.png")
        plt.close()

    def moving_average():
        plt.figure()
        plt.scatter(
            daily_data["Date"],
            daily_data["Drinks"],
            alpha=0.5,
            label="Daily Drinks",
        )
        plt.plot(
            daily_data["Date"],
            daily_data["Moving_Avg"],
            color="red",
            label="7-Day Moving Average",
        )
        plt.title("Daily Drinks Over Time")
        plt.xlabel("Date")
        plt.ylabel("Drinks")
        plt.legend()
        plt.savefig("./plots/daily/moving_average_daily.png")
        plt.close()

    def log_scale():
        non_zero_daily_data = daily_data[daily_data["Drinks"] > 0]
        plt.figure()
        plt.scatter(
            non_zero_daily_data["Date"],
            non_zero_daily_data["Drinks"],
            alpha=0.5,
            label="Daily Drinks",
        )
        plt.yscale("log")
        plt.title("Daily Drinks Over Time (Log Scale)")
        plt.xlabel("Date")
        plt.ylabel("Drinks (Log Scale)")
        plt.legend()
        plt.grid(True, which="both", axis="y", linestyle="--", linewidth=0.5)
        plt.savefig("./plots/daily/log_scale_daily.png")
        plt.close()

    def calendar():
        # Calendar heatmap
        plt.figure(figsize=(16, 8))
        calendar_data = daily_data.pivot_table(
            index=daily_data["Date"].dt.month,
            columns=daily_data["Date"].dt.day,
            values="Drinks",
            fill_value=0,
        )
        sns.heatmap(
            calendar_data, cmap="YlGnBu", cbar_kws={"label": "Number of Drinks"}
        )
        plt.title("Calendar Heatmap of Daily Drinks")
        plt.xlabel("Day of the Month")
        plt.ylabel("Month")
        plt.savefig("./plots/daily/calendar_heatmap.png")
        plt.close()

    histogram()
    cluster()
    violin()
    moving_average()
    log_scale()
    calendar()


def weekly(data):
    os.makedirs("./plots/weekly", exist_ok=True)

    # Aggregate weekly
    weekly_data = data.resample("W-SUN", on="Date").sum().reset_index()
    weekly_data["Moving_Avg"] = calculate_moving_average(
        weekly_data["Drinks"], window=5
    )

    def histogram():
        plt.figure()
        plt.hist(weekly_data["Drinks"], edgecolor="black")
        plt.title("Histogram of Weekly Drinks")
        plt.xlabel("Weekly Drinks")
        plt.ylabel("Frequency")
        plt.savefig("./plots/weekly/histogram_weekly.png")
        plt.close()

    def boxplot():
        plt.figure()
        plt.boxplot(
            weekly_data["Drinks"],
            vert=False,
            patch_artist=True,
        )
        plt.title("Weekly Drinks Box Plot")
        plt.xlabel("Weekly Drinks")
        plt.yticks([])
        plt.savefig("./plots/weekly/boxplot_weekly.png")
        plt.close()

    def moving_average():
        plt.figure()
        plt.scatter(
            weekly_data["Date"],
            weekly_data["Drinks"],
            label="Weekly Drinks",
            alpha=0.5,
        )
        plt.plot(
            weekly_data["Date"],
            weekly_data["Moving_Avg"],
            color="red",
            label="5-Week Moving Average",
        )
        plt.title("Weekly Drinks Over Time")
        plt.xlabel("Date")
        plt.ylabel("Drinks")
        plt.legend()
        plt.savefig("./plots/weekly/moving_average_weekly.png")
        plt.close()

    def bar_graph():
        plt.figure()
        plt.bar(weekly_data["Date"], weekly_data["Drinks"], width=5)
        plt.title("Drinks per Week")
        plt.xlabel("Week")
        plt.ylabel("Total Drinks")
        plt.xticks(
            weekly_data["Date"][::4],
            weekly_data["Date"].dt.strftime("%Y-%m-%d")[::4],
            rotation=45,
        )
        plt.tight_layout()
        plt.savefig("./plots/weekly/bar_graph_weekly.png")
        plt.close()

    histogram()
    boxplot()
    moving_average()
    bar_graph()


def monthly(data):
    os.makedirs("./plots/monthly", exist_ok=True)

    # Aggregate monthly
    monthly_data = data.resample("ME", on="Date").sum().reset_index()
    monthly_data["Moving_Avg"] = calculate_moving_average(
        monthly_data["Drinks"], window=3
    )

    def boxplot():
        plt.figure()
        plt.boxplot(
            monthly_data["Drinks"],
            vert=False,
            patch_artist=True,
        )
        plt.title("Monthly Drinks Box Plot")
        plt.xlabel("Monthly Drinks")
        plt.yticks([])
        plt.xlim(left=0)
        plt.savefig("./plots/monthly/boxplot_monthly.png")
        plt.close()

    def bar_graph():
        plt.figure()
        plt.bar(
            monthly_data["Date"],
            monthly_data["Drinks"],
            width=20,
        )
        plt.title("Drinks per Month in 2024")
        plt.xlabel("Month")
        plt.ylabel("Total Drinks")
        plt.xticks(
            monthly_data["Date"], monthly_data["Date"].dt.strftime("%B"), rotation=45
        )
        plt.savefig("./plots/monthly/bar_graph_monthly.png")
        plt.close()

    boxplot()
    bar_graph()


def print_stats(data):
    daily_data = data.resample("D", on="Date").sum().reset_index()
    total_drinks = daily_data["Drinks"].sum()
    days_drinking = (daily_data["Drinks"] > 0).sum()
    days_not_drinking = (daily_data["Drinks"] == 0).sum()
    percent_days_drinking = (days_drinking / len(daily_data)) * 100
    mean_drinks = daily_data["Drinks"].mean()
    mean_drinks_on_drinking_days = daily_data[daily_data["Drinks"] > 0]["Drinks"].mean()
    average_drinks_per_weekday = (
        daily_data.groupby(daily_data["Date"].dt.day_name())["Drinks"]
        .mean()
        .reindex(
            [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
        )
    )

    # Calculate longest streaks
    daily_data["Drinking"] = daily_data["Drinks"] > 0
    daily_data["Sober_Streak"] = (
        daily_data["Drinking"] != daily_data["Drinking"].shift()
    ).cumsum()
    sober_streaks = (
        daily_data[daily_data["Drinking"] == False].groupby("Sober_Streak").size()
    )
    drinking_streaks = (
        daily_data[daily_data["Drinking"] == True].groupby("Sober_Streak").size()
    )
    longest_sober_streak = sober_streaks.max() if not sober_streaks.empty else 0
    longest_drinking_streak = (
        drinking_streaks.max() if not drinking_streaks.empty else 0
    )
    weekly_data = data.resample("W-SUN", on="Date").sum().reset_index()
    at_least_20 = daily_data[daily_data["Drinks"] >= 20]["Date"]
    highest_week = weekly_data.loc[weekly_data["Drinks"].idxmax()]

    print(f"Total drinks: {total_drinks}")
    print(f"Days drinking: {days_drinking}")
    print(f"Days not drinking: {days_not_drinking}")
    print(f"% of days drinking: {percent_days_drinking:.2f}%")
    print(f"Mean drinks per day: {mean_drinks:.2f}")
    print(f"Mean drinks on drinking days: {mean_drinks_on_drinking_days:.2f}")
    print("Average drinks per weekday:")
    for day, avg in average_drinks_per_weekday.items():
        print(f"  {day}: {avg:.2f}")
    print(f"Longest sober streak: {longest_sober_streak} days")
    print(f"Longest drinking streak: {longest_drinking_streak} days")
    print("Dates with 20+ drinks:")
    for date in at_least_20:
        print("  " + date.strftime("%Y-%m-%d"))
    print(
        f"Week with highest drinks: W{highest_week['Date'].strftime('%V')} with {highest_week['Drinks']} drinks"
    )


def main():
    plt.rcParams["figure.figsize"] = (12, 6)

    parser = argparse.ArgumentParser(description="Alcohol consumption analysis")
    parser.add_argument(
        "-d",
        "--data_path",
        type=str,
        default="./data.csv",
        help="Path to the CSV file containing the data",
    )
    args = parser.parse_args()

    os.environ["QT_QPA_PLATFORM"] = "xcb"
    os.makedirs("./plots", exist_ok=True)

    data = load_and_prepare_data(args.data_path)

    daily(data)
    weekdays(data)
    weekly(data)
    monthly(data)

    print_stats(data)


if __name__ == "__main__":
    main()
