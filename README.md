# Alcohol Analysis

This repo tracks and performs some data visualization on my drinking habits.

## Data Collection
Data is collected by me manually entering it into a spreadsheet on my Google Drive. Usually, I tally on my left hand for each drink I have in a day, and then enter data the next day. For especially heavy days (~20+ drinks), the data is often also an estimate based on how much I think I would have drank the night before. There are numerous significant issues with this data collection. 

Firstly, what constitutes a "drink" is not standardized. A beer in a bar almost always counts, as does a bottled beer, a shot, or a glass of wine, or a cocktail. It is obvious that these will have significantly different sizes depending on in what context I am drinking. I assume that I generally pour myself a little more than a "standard" drink when I pour for myself. 

Secondly, data is self-reported. Depending on my mood I have an incentive to over- or under-report my drinking. I might want to seem more impressive to my drinking friends, or more healthy to soothe my conscience. This is made worse by the fact that I am necessarily often drunk when recording data, which exacerbates this effect.

Without any data to inform this, I would estimate a margin of error of 20% to be fair. However, this also means that days with zero or low counts are quite accurate. I am reasonably confident that the days on which I wrote down zero drinks I actually did not have any drinks. In this context, a sip of beer from someone else for example does not count.

## Script
The `alcohol-analysis.py` script is used to aggregate and visualize data. You can import the conda environment I used using `environment.yml`. The script can take one command-line argument: `-d` or `--data_path` to specify the path to the data `csv` file. If no custom path is provided it will attempt to use `./data.csv`. Plots are saved to `./plots/{timespan}/{name}`.

The following plots are created:
- Daily:
 - Calendar Heatmap
 - Cluster Plot
 - Histogram
 - Time Series with 7-day moving average
 - Violin Plot
- By Weekdays:
 - Box Plots for each day of the week
 - Bar Chart per day of the week
- Weekly (Mon-Sun):
 - Bar Graph for total drinks each week
 - Box Plot for drinks per week
 - Histogram
 - Time Series with 5-week moving average
- Monthly
 - Bar Graph for total drinks each month
 - Box Plot for drinks per month

Additionally, the script prints a selection of statistics to `stdout`, such as average drinks per day or day of the week, total days drinking, total days not drinking, longest sober and drinking streaks, and more.