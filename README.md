# Analysis of US Rental Market
**Project Overview and Objectives:**

Explore the US apartment rental landscape to identify distinct rental segments and their defining characteristics.

**Data Overview & Preparation Steps:**

Source: University of Irvine, Machine Learning repository. https://archive.ics.uci.edu/dataset/555/apartment+for+rent+classified!

The dataset comprises a compilation of apartment listings available for rent across the United States as of December 25, 2019, predating the onset of the pandemic. The raw dataset contains approximately 100,000 records; after cleaning, 99,189 records were retained for analysis.

**Methodology Overview** :

1. Performed data exploration and cleaning techniques using pandas and numpy libraries. Refer to US Rental Market power point presentation for more details.
2. Analyzed apartment amenities and sizes (i.e. 1bed/1ba , 2 beds/2bas etc..)
   - Sports amenities: Pool, Gym, Tennis, Basketball, Golf
   - Outdoor amenities: Patio/Deck, Clubhouse, Playground
   - Convenience amenities: Parking, Garbage Disposal, Washer Dryer, AC, Elevator, Dishwasher, Storage, Gated, Refrigerator, Cable or Satellite, Internet Access
   - Luxury amenities: Fireplace, Wood Floors, View, Doorman, Luxury, Hot Tub
3. Utilized Scikit Learn's One-Hot Encoding and StandardScaler techniques to normalize and standardize the dataset.
4. Applied unsupervised learning techniques (i.e. KMeans Clustering and PCA) to determine the market segments
   - KMeans Outcome: 2 segments identified
   - Principal Components Analysis Outcome: 2 segments identified with an Explained Variance Ratio of 62%.
5. Employed PyCaret and the XGBoost algorithm to enhance clustering techniques and determine feature importance
   - Achieved an accuracy rate = 99%
6. Built an interactive Streamlit dashboard (SRC/app.py) for exploring the rental segments by state, city, price range, and cluster, with property map and amenity composition charts.

**Results & Outcomes:**

Classification based by rental price, square feet, sports, outdoor, luxury, convenience amenities and geographical location.
2 segments identified (99,189 total properties):

A- Cluster 0: Essential Rentals (81,312 properties — 82% of total)
- Average Rent: $1,550
- Median Rent: $1,375
- Median SQ Feet: 905
- Median count of sports amenities: 0
- Median count of outdoor amenities: 0
- Median Count of convenience amenities: 1
- Median Count of luxury amenities: 0

B- Cluster 1: Amenity-Packed Rentals (17,877 properties — 18% of total)
- Average Rent: $1,415
- Median Rent: $1,250
- Median Sq Feet: 880
- Median count of sports amenities: 2
- Median count of outdoor amenities: 1
- Median Count of convenience amenities: 5
- Median Count of luxury amenities: 0

**Conclusion:**

The American rental market is predominantly a Cluster 0 (Essential Rentals) market at 82% of all listings, though both segments are present in all cities, varying by neighborhood. Cluster 0 rentals are characterized by spacious apartments with fewer amenities. In contrast, Cluster 1 (Amenity-Packed Rentals) are characterized by smaller apartments with more amenities and are primarily located in the Northeast region of the country.

**Interactive Dashboard:**

An interactive Streamlit dashboard is available at: https://ellac12345.github.io/US_Rental_Market/

The dashboard allows users to filter by state, city, price range, and cluster to explore property distribution on a map and view amenity composition by segment.
