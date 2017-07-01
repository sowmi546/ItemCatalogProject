
## Step1 :
Navigate to 'ItemCatalogProject' folder and first run the file 'db_setup.py' 
Command :
`python db_setup.py`

This would create the database 'catalog.db' file.

## Step2 :
Now run the below command to populate with test data
Command :
`python lotofcatitems.py`

Test message 'added category and items!' gets printed once the records are created in tables (User, CatalogItem and Category)

## Step3 :
Now run the below command to start the local server on port 8000
`python application.py`

For login I am using Google plus to login, and also using normal login.
I am creating new users by using 'Signup' option.

JSON can be seen at the corresponding URLs  - Please refer to '# JSON APIs to view Catalog Information' in application.py file
