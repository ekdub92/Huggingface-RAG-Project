from sklearn.feature_extraction.text import TfidfVectorizer
from elasticsearch import Elasticsearch, helpers

# load dataset
data_path = 'huggingface.transformers'
lines = open(data_path, 'r').readlines()

# compute TF-IDF
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(lines)

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
        "content": line,
        "content_vector": tfidf_matrix[index].toarray().flatten().tolist()
    }
} for index, line in enumerate(lines)]

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
