-- LOCAL FOOD WASTAGE MANAGEMENT SYSTEM

-- To Create the Database.
DROP DATABASE food_wastage;
CREATE DATABASE food_wastage;

-- Use Database and see all 4 tables.
USE food_wastage;
SHOW TABLES;

-- Check all Data are perfectly Stored or not.
SELECT COUNT(*) AS Total_Providers FROM providers;
SELECT COUNT(*) AS Total_Receivers FROM receivers;
SELECT COUNT(*) AS Total_Food_Listings FROM food_listings;
SELECT COUNT(*) AS Total_Claims FROM claims;

-- See the proper Data Format.
SELECT * FROM providers LIMIT 5;
SELECT * FROM food_listings LIMIT 5;

-- Q1. Identify the top 5 cities with the highest number of food listings.
SELECT 
    Location AS City_Name, 
    COUNT(Food_ID) AS Total_Active_Listings 
FROM food_listings 
GROUP BY Location 
ORDER BY Total_Active_Listings DESC 
LIMIT 5;

-- Q2. Find the total volume of food donated by each provider category.
SELECT 
    Provider_Type AS Business_Category, 
    SUM(Quantity) AS Total_Volume_Donated 
FROM food_listings 
GROUP BY Provider_Type 
ORDER BY Total_Volume_Donated DESC;

-- Q3. What is the success rate of claims (count and percentage of each status)?
SELECT 
    Status, 
    COUNT(Claim_ID) AS Claim_Count, 
    ROUND((COUNT(Claim_ID) * 100.0 / (SELECT COUNT(*) FROM claims)), 2) AS Percentage_Share 
FROM claims 
GROUP BY Status;

-- Q4. Which receiver types claim the most food in terms of total quantity?
SELECT 
    r.Type AS Receiver_Category, 
    SUM(f.Quantity) AS Total_Claimed_Quantity 
FROM claims c 
INNER JOIN receivers r ON c.Receiver_ID = r.Receiver_ID 
INNER JOIN food_listings f ON c.Food_ID = f.Food_ID 
WHERE c.Status = 'Completed' 
GROUP BY r.Type 
ORDER BY Total_Claimed_Quantity DESC;

-- Q5. Find the top 3 highest-contributing providers by their actual names.
WITH ProviderTotals AS (
    SELECT Provider_ID, SUM(Quantity) AS Total_Food 
    FROM food_listings 
    GROUP BY Provider_ID
)
SELECT 
    p.Name AS Provider_Name, 
    pt.Total_Food 
FROM ProviderTotals pt 
INNER JOIN providers p ON pt.Provider_ID = p.Provider_ID 
ORDER BY pt.Total_Food DESC 
LIMIT 3;

-- Q6. Providers by city: Find the distribution of providers across different cities.
SELECT 
    City, 
    COUNT(Provider_ID) AS Total_Providers,
    ROUND((COUNT(Provider_ID) * 100.0 / (SELECT COUNT(*) FROM providers)), 2) AS Percentage_Share
FROM providers 
GROUP BY City 
ORDER BY Total_Providers DESC;

-- Q7. Receivers by city: Analyze the presence of receivers in various cities.
SELECT 
    City, 
    COUNT(Receiver_ID) AS Total_Receivers
FROM receivers 
GROUP BY City 
ORDER BY Total_Receivers DESC;

-- Q8. Most common food type: Identify the most frequently listed food types on the platform.
SELECT 
    Food_Type, 
    COUNT(Food_ID) AS Listing_Frequency,
    SUM(Quantity) AS Total_Available_Quantity
FROM food_listings 
GROUP BY Food_Type 
ORDER BY Listing_Frequency DESC;

-- Q9. Average quantity claimed: Calculate the average food quantity successfully claimed per transaction.
SELECT 
    ROUND(AVG(f.Quantity), 2) AS Average_Claimed_Quantity 
FROM claims c
INNER JOIN food_listings f ON c.Food_ID = f.Food_ID
WHERE c.Status = 'Completed';

-- Q10. Most claimed meal type: Determine which meal type is claimed the most.
SELECT 
    f.Meal_Type, 
    SUM(f.Quantity) AS Total_Quantity_Claimed 
FROM claims c
INNER JOIN food_listings f ON c.Food_ID = f.Food_ID
WHERE c.Status = 'Completed'
GROUP BY f.Meal_Type 
ORDER BY Total_Quantity_Claimed DESC
LIMIT 1;

-- Q11. Most claimed food: Find out which specific food items are claimed the most by volume.
SELECT 
    f.Food_Name, 
    COUNT(c.Claim_ID) AS Times_Claimed, 
    SUM(f.Quantity) AS Total_Volume_Claimed 
FROM claims c 
INNER JOIN food_listings f ON c.Food_ID = f.Food_ID 
WHERE c.Status = 'Completed' 
GROUP BY f.Food_Name 
ORDER BY Total_Volume_Claimed DESC 
LIMIT 5;

-- Q12. Provider Analysis: Which provider has the highest number of successful (Completed) claims?
SELECT 
    p.Name AS Provider_Name, 
    COUNT(c.Claim_ID) AS Successful_Transactions 
FROM claims c 
INNER JOIN food_listings f ON c.Food_ID = f.Food_ID 
INNER JOIN providers p ON f.Provider_ID = p.Provider_ID 
WHERE c.Status = 'Completed' 
GROUP BY p.Name 
ORDER BY Successful_Transactions DESC 
LIMIT 5;    

-- Q13. Total donated quantity by provider: Evaluate the overall efficiency of providers. 
SELECT 
    p.Name, 
    p.Type AS Business_Category, 
    SUM(f.Quantity) AS Total_Donated_Quantity 
FROM providers p 
INNER JOIN food_listings f ON p.Provider_ID = f.Provider_ID 
GROUP BY p.Name, p.Type 
ORDER BY Total_Donated_Quantity DESC 
LIMIT 5;

-- Q14. Demand Analysis: Which city has the highest food demand based on the volume of claims?
SELECT 
    r.City, 
    COUNT(c.Claim_ID) AS Total_Claims_Made, 
    SUM(f.Quantity) AS Total_Volume_Demanded 
FROM claims c 
INNER JOIN receivers r ON c.Receiver_ID = r.Receiver_ID 
INNER JOIN food_listings f ON c.Food_ID = f.Food_ID 
GROUP BY r.City 
ORDER BY Total_Volume_Demanded DESC 
LIMIT 5;

-- Q15. Food Waste: Which meal type gets wasted the most (Highest volume of Cancelled/Pending claims)?
SELECT 
    f.Meal_Type, 
    COUNT(c.Claim_ID) AS Unfulfilled_Claims_Count, 
    SUM(f.Quantity) AS Wasted_Quantity 
FROM claims c 
INNER JOIN food_listings f ON c.Food_ID = f.Food_ID 
WHERE c.Status IN ('Cancelled', 'Pending') 
GROUP BY f.Meal_Type 
ORDER BY Wasted_Quantity DESC;