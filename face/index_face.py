import boto3

bucket = "bonduelle-betterave-faces"
collection = "BETTERAVE_FACES"

client = boto3.client('rekognition')
print "* Delete collection (if exists)"
try:
	client.delete_collection(CollectionId=collection)
	print "         -->  Ok"
except:
	print "         --> Collection did not exist"

print "* Create collection"
response = client.create_collection(CollectionId=collection)
print "         -->  Ok"


s3 = boto3.resource('s3')
my_bucket = s3.Bucket(bucket)

for file in my_bucket.objects.all():
	name = file.key.split('.')[0].split('_')[0]
	print "* Indexing file : %s, for name %s" % (file.key,name)
	response = client.index_faces(ExternalImageId=name,Image={"S3Object": {"Bucket": bucket,"Name":file.key}}, CollectionId="BETTERAVE_FACES")
	if response['ResponseMetadata']['HTTPStatusCode']==200:
		print "         --> Indexation OK"
	else:
		print "         Error %i " % (response['ResponseMetadata']['HTTPStatusCode'])

print "----------------------------"
print "Listing all index"
response = client.list_faces(CollectionId=collection)
index = {}
for face in response['Faces']:
	index[face['ExternalImageId']] = face['ImageId']
for face in index.keys():
	print "        - id : %s / %s" % (face,index[face])

