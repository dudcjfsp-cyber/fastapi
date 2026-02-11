# MySQL Migration Walkthrough

The application's data source has been successfully migrated from SQLite to **MySQL**.

## Configuration
- **Database**: `pk_fk_practice`
- **User**: `root`
- **Port**: `3306`
- **Host**: `localhost`

## Changes Made
1. **Infrastructure**: Installed `mysql-connector-python`.
2. **Environment**: Updated `.env` with MySQL credentials.
3. **Data Layer**: Modified `data.py` to use `mysql.connector`.
4. **Schema**: Provided `create_members.sql` for creating the `members` table in MySQL.

## Verification
- **FastAPI Hello**: http://localhost:8000/docs
- **MCP Server**: Running on port 8002
- **API Server**: Running on port 8004

### How to Verify
1. Ensure the `members` table exists in your MySQL database `pk_fk_practice` and has data (use `create_members.sql` if needed).
2. Visit `http://localhost:8000/members` to see the list of members fetched from MySQL.
3. Visit `http://localhost:8000/members/ideabong` to see member details.

## How to Manage Data (Add/Edit/Delete)

You can manage the database directly using a tool like **MySQL Workbench** or by running Python scripts.

### Option 1: Using Python Script (Recommended for Beginners)
I created a script called `add_member.py`. You can modify it to add more members.

1. Open `add_member.py`.
2. Change the values in this line:
   ```python
   val = ('newbie', '신입', '무관', '캐주얼', 'Home')
   ```
   To something else, for example:
   ```python
   val = ('jini', '지니', '여성', '오피스 룩', 'Pangyo')
   ```
3. Run the script: `python add_member.py`

### Option 2: Using SQL (Advanced)
Run this SQL query in your database tool (MySQL Workbench):
```sql
INSERT INTO members (username, name, gender, style, location) 
VALUES ('new_user', '새로운 유저', '여성', '모던 시크', 'Jeju');
```

### Option 3: Update/Delete
**Update**:
```sql
UPDATE members 
SET style = '스트릿 패션', location = 'Gangnam' 
WHERE username = 'ideabong';
```

**Delete**:
```sql
DELETE FROM members WHERE username = 'newbie';
```

After running any of these commands, simply refresh the API page (e.g., `http://localhost:8000/members`) to see the changes immediately.
