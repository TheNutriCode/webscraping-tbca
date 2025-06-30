# Optimized Food Nutrient Database Structure

This document explains the optimized database structure implemented for the food nutrient database.

## Key Changes

The database has been restructured to use a **column-based approach** instead of the previous Entity-Attribute-Value (EAV) model. This offers several advantages:

1. **Better Performance**: All nutrient data for a food is stored in a single row
2. **Typed Data**: Nutrients are stored with appropriate DECIMAL types instead of VARCHAR
3. **Simpler Queries**: No need for multiple JOINs to get all nutrient data
4. **Enhanced Data Integrity**: Consistent nutrient names and units

## Database Schema

The database now includes the following key tables:

1. **foods**: Unchanged - stores basic food information
2. **food_variations**: Unchanged - stores variations of foods
3. **nutrients**: New table - stores metadata about nutrients (name, unit, category)
4. **food_variation_nutrients**: New table - stores all nutrients for each food variation as columns
5. **food_nutrients**: Legacy table - kept for backward compatibility

## Migration Process

To migrate data from the old structure to the new one:

1. Run the database schema update script to create the new tables
2. Run the migration script to:
   - Populate the nutrients reference table
   - Transfer data from food_nutrients to food_variation_nutrients

```bash
# Run the migration script
python src/migrate_data.py
```

## Using the New Structure

### Example Queries

See `src/example_queries.sql` for a comprehensive set of example queries that demonstrate how to effectively use the new database structure.

Some examples include:

- Getting complete nutrient profiles for foods
- Finding foods high in specific nutrients
- Comparing nutrient content across food groups
- Calculating nutrient density scores

### Code Updates

The `webscraping.py` file has been updated to insert data into both:

1. The legacy `food_nutrients` table (for backward compatibility)
2. The new `food_variation_nutrients` table (for performance)

This ensures that existing code continues to work while new code can take advantage of the optimized structure.

## Advantages of the New Structure

1. **Query Simplification**: Get all nutrients for a food with a single query
2. **Performance**: Faster data retrieval, especially for complete nutrient profiles
3. **Data Integrity**: Proper data types and consistent nutrient names
4. **Analysis Ready**: Easier to perform statistical analysis and reporting

## Backward Compatibility

The original `food_nutrients` table is still maintained and populated alongside the new structure, ensuring backward compatibility with existing code.

## How to Extend

To add new nutrients to the system:

1. Add the new column to the `food_variation_nutrients` table
2. Add the nutrient to the nutrient mapping in `webscraping.py`
3. Add the nutrient to the migration script if needed

This approach offers a good balance between performance and flexibility.
