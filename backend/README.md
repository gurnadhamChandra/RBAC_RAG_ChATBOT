# Internal chatbot with role based access control

# run server 
uvicorn app.main:app --reload
please ensure you run the /build_vectors endpoint in  `yourport/docs` ,it will run the vector db local so that apis will fetch data and insert data to local db 
### Roles Provided
 - **engineering**
 - **finance**
 - **general**
 - **hr**
 - **marketing**
