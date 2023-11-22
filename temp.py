import asyncio
import asyncpg

async def fetch_rows():
    # Replace the connection parameters with your own
    dsn = "postgres://pricetrackerpostgre_9qzk_user:nzOy2XsY6XwRARqkcXhhR4W52KNhjEjP@dpg-cldgpnngsrdc73fl1qag-a.frankfurt-postgres.render.com/pricetrackerpostgre_9qzk"
    

    # Establish a connection to the database
    connection = await asyncpg.connect(dsn)

    try:
        # Execute a SQL query to fetch rows
        product = 'Samsung'
        query = f"select min_price from min_price where product = '{product}';"
        row = await connection.fetchrow(query)
        print(row['min_price'])

        # rows=  dict(row)if row else None
        # print(rows)
    finally:
        # Close the connection
        await connection.close()

if __name__ == "__main__":
    # Run the async function
    asyncio.run(fetch_rows())