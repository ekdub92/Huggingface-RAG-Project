import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from elasticsearch import Elasticsearch, helpers
import json

# load dataset
raw_path = 'huggingface.transformers'
lines = open(raw_path, 'r').readlines()

# transfer as json
df = pd.DataFrame(lines, columns=['sentence'])
json_data = df.to_json(orient='records')
records = json.loads(json_data)

# compute TF-IDF
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df['sentence'])

# initialize elasticsearch client
client = Elasticsearch('http://127.0.0.1:9201')

# define the index configuration with dense_vector type
index_config = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "content": {
                "type": "text"
            },
            "content_vector": {
                "type": "dense_vector",
                "dims": tfidf_matrix.shape[1]
            }
        }
    }
}

# create the index
client.indices.create(index='tfidf_vector_index', body=index_config, ignore=400)

# prepare documents for indexing
docs = [{
    "_index": "tfidf_vector_index",
    "_source": {
        "content": line['sentence'],
        "content_vector": tfidf_matrix[index].toarray().flatten().tolist()
    }
} for index, line in enumerate(records)]
print(docs)
# bulk indexing the documents 
helpers.bulk(client, docs)

# example vector inference 
query = ""
query_vector = vectorizer.transform([query]).toarray()[0].tolist()

# define the vector similarity query 
script_query = {
    "script_score": {
        "query": {"match_all": {}},
        "script": {
            "source": "cosineSimilarity(params.query_vector, doc['content_vector'])",
            "params": {"query_vector": query_vector}
        }
    }
}

# perform the search 
response = client.search(
    index="tfidf_vector_index",
    query=script_query,
    size=10,
    _source_includes=["content"]
)

# display results
for hit in response['hits']['hits']:
    print(f'Content: {hit["_source"]["content"]}, Score: {hit["_score"]}')
