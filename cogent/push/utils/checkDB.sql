#Check Our Two Dtabases match (PUSH)

/*
#Look for Missing Deployments
SELECT * FROM test.Deployment as TST 
LEFT OUTER JOIN mainStore.Deployment as MS
ON TST.name = MS.name
WHERE MS.id is NULL;
*/

/*
SELECT * FROM test.House as TST 
LEFT OUTER JOIN mainStore.House as MS
ON TST.address = MS.address
WHERE MS.id is NULL;
*/

SELECT * FROM test.Room as TST 
JOIN mainStore.Room as MS
ON TST.id = MS.id;
