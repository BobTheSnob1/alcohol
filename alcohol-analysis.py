import pandas as pd
import os
import argparse
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.colors import ListedColormap


def load_and_prepare_data(file_path):
    """Load the CSV file and prepare the data."""
    data = pd.read_csv(file_path)
    data["Date"] = pd.to_datetime(data["Date"], format="%d.%m.%Y")
    return data


def calculate_moving_average(data, window, center=True):
    """Calculate the moving average for a given window size."""
    return data.rolling(window=window, center=center).mean()


def daily(data):
    os.makedirs("./plots/daily", exist_ok=True)

    # Aggregate daily
    daily_data = data.resample("D", on="Date").sum().reset_index()
    daily_data["Moving_Avg"] = calculate_moving_average(daily_data["Drinks"], window=7)

    # Histogram
    plt.figure()
    plt.hist(daily_data["Drinks"])
    plt.title("Histogram of Daily Drinks")
    plt.xlabel("Daily Drinks")
    plt.ylabel("Frequency")
    plt.savefig("./plots/daily/histogram_daily.png")
    plt.close()

    # Cluster plot
    jitter = np.random.uniform(-0.1, 0.1, len(daily_data))
    plt.figure()
    plt.scatter(
        daily_data["Drinks"], jitter, alpha=0.7, color="green", edgecolor="black", s=100
    )
    plt.title("Daily Drinks Cluster Plot")
    plt.xlabel("Daily Drinks")
    plt.ylabel("Jitter (for visualization only)")
    plt.yticks([])  # Remove Y-axis labels as they don't have a specific meaning
    plt.savefig("./plots/daily/cluster_plot_daily.png")
    plt.close()

    # Time series
    plt.figure()
    plt.scatter(
        daily_data["Date"],
        daily_data["Drinks"],
        color="green",
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

    # Time series on a log scale (omit zero drink days)
    non_zero_daily_data = daily_data[daily_data["Drinks"] > 0]
    plt.figure()
    plt.scatter(
        non_zero_daily_data["Date"],
        non_zero_daily_data["Drinks"],
        color="green",
        alpha=0.5,
        label="Daily Drinks",
    )
    plt.yscale("log")
    plt.title("Daily Drinks Over Time (Log Scale)")
    plt.xlabel("Date")
    plt.ylabel("Drinks (Log Scale)")
    plt.legend()
    plt.savefig("./plots/daily/log_scale_daily.png")
    plt.close()

    # Print statistics
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

    # Mean drinks per weekday bar plot
    plt.figure()
    plt.bar(
        average_drinks_per_weekday.index,
        average_drinks_per_weekday.values,
        color="skyblue",
    )
    plt.title("Average Drinks per Weekday")
    plt.xlabel("Weekday")
    plt.ylabel("Average Drinks")
    plt.savefig("./plots/daily/drinks_per_weekday.png")
    plt.close()

    # Calendar heatmap

    # Create a pivot table with days as rows and months as columns
    calendar_data = daily_data.pivot("Date", "Date", "Drinks").fillna(0)

    # Create a custom colormap
    cmap = ListedColormap(sns.color_palette("YlGnBu", 10))

    plt.figure(figsize=(15, 10))
    sns.heatmap(
        calendar_data,
        cmap=cmap,
        cbar_kws={"label": "Number of Drinks"},
        linewidths=0.1,
        linecolor="black",
    )
    plt.title("Calendar Heatmap of Daily Drinks")
    plt.xlabel("Month")
    plt.ylabel("Day")
    plt.savefig("./plots/daily/calendar_heatmap_daily.png")
    plt.close()


def weekly(data):
    os.makedirs("./plots/weekly", exist_ok=True)

    # Aggregate weekly
    weekly_data = data.resample("W-Mon", on="Date").sum().reset_index()
    weekly_data["Moving_Avg"] = calculate_moving_average(
        weekly_data["Drinks"], window=5
    )

    # Histogram
    plt.figure()
    plt.hist(weekly_data["Drinks"], color="blue", alpha=0.7, edgecolor="black")
    plt.title("Histogram of Weekly Drinks")
    plt.xlabel("Weekly Drinks")
    plt.ylabel("Frequency")
    plt.savefig("./plots/weekly/histogram_weekly.png")
    plt.close()

    # Boxplot
    plt.figure()
    plt.boxplot(
        weekly_data["Drinks"],
        vert=False,
        patch_artist=True,
        boxprops=dict(facecolor="lightblue"),
    )
    plt.title("Weekly Drinks Box Plot")
    plt.xlabel("Weekly Drinks")
    plt.yticks([])
    plt.savefig("./plots/weekly/boxplot_weekly.png")
    plt.close()

    # Time series
    plt.figure()
    plt.scatter(
        weekly_data["Date"],
        weekly_data["Drinks"],
        color="blue",
        alpha=0.6,
        label="Weekly Drinks",
    )
    plt.plot(
        weekly_data["Date"],
        weekly_data["Moving_Avg"],
        color="orange",
        label="5-Week Moving Average",
    )
    plt.title("Weekly Drinks Over Time")
    plt.xlabel("Date")
    plt.ylabel("Drinks")
    plt.legend()
    plt.savefig("./plots/weekly/moving_average_weekly.png")
    plt.close()

    # Bar graph
    plt.figure()
    plt.bar(
        weekly_data["Date"], weekly_data["Drinks"], color="blue", alpha=0.7, width=5
    )
    plt.title("Drinks per Week")
    plt.xlabel("Week")
    plt.ylabel("Total Drinks")
    plt.xticks(
        weekly_data["Date"][::4],
        weekly_data["Date"].dt.strftime("%Y-%m-%d")[::4],
        rotation=45,
    )
    plt.savefig("./plots/weekly/bar_graph_weekly.png")
    plt.close()


def monthly(data):
    os.makedirs("./plots/monthly", exist_ok=True)

    # Aggregate monthly
    monthly_data = data.resample("ME", on="Date").sum().reset_index()
    monthly_data["Moving_Avg"] = calculate_moving_average(
        monthly_data["Drinks"], window=3
    )

    # Boxplot
    plt.figure()
    plt.boxplot(
        monthly_data["Drinks"],
        vert=False,
        patch_artist=True,
        boxprops=dict(facecolor="plum"),
    )
    plt.title("Monthly Drinks Box Plot")
    plt.xlabel("Monthly Drinks")
    plt.yticks([])
    plt.savefig("./plots/monthly/boxplot_monthly.png")
    plt.close()

    # Bar graph
    plt.figure()
    plt.bar(
        monthly_data["Date"],
        monthly_data["Drinks"],
        color="purple",
        alpha=0.7,
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


def main():
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
    weekly(data)
    monthly(data)


if __name__ == "__main__":
    main()
