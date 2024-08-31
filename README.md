# NLP Search Project
- Authors: 모두연 짱짱맨들
- Project: 허깅페이스 공식 문서 검색 시스템 
- Last updated: 2024-08-30
- Status: Draft 
- Target readers: 모두연 멤버

## Context and scope
- 방대한 양의 공식 문서를 단기간에 소화하거나, 원하는 정보를 찾는 것이 어려움
- 정확한 문자를 입력하지 않으면 내부에서 제공하는 검색 시스템에서 찾아지지 않음
- 이를 RAG 를 이용하여 벡터 서치로 해결하고자 함

## Goals and non-goals
이 시스템을 통하여 달성하고자 하는 목표는 다음과 같습니다.
- 공식 문서의 내용을 쉽게 찾을 수 있도록 함
- 검색한 문자열 그대로의 내용이 아니더라도 검색이 되도록 함

## Overview
여기에서는 설계의 개요를 간단히 설명합니다.
- 화면 : 질문 입력 -> 결과 반환
- DB 데이터 처리 : 공식 문서 크롤링  -> 전처리 -> 토큰화 -> 벡터 스토어 저장 (임베딩) 
- 유저 사용 시나리오 : 쿼리 입력 -> 토큰화 -> 벡터 스토어에서 관련성 높은 문서 서치 -> 서치된 문서로 모델이 응답 생성 -> 결과 반환

## Detailed design
### UI design

-> leonardo.Ai로 화면 생성해봤는데 디자인이 뭔가 구린 것 같기도 하고… 더 좋은 게 있으면 바꿀 예정 

### System-context-diagram (relationship to other systems)
다이어그램은 이 시스템이 어떠한 환경에서 다른 컴포넌트들과 어떻게 연관되는지를 보여줍니다.


### APIs
- 서버 API : (server ip):(server port) 
- 모델 서빙 API : (server ip):(serving port) 
- (옵션) 모델 사용법 기재한  swagger API : (server ip):(serving port)/docs 

### Data storage
- 벡터 DB로 ElasticSearch 선택 (변동 가능성 있음) 
- 스키마 구성 : class를 생성하여 문서를 저장할 변수를 만들 예정 (추후 프로젝트 구현을 시작해봐야 다른 변수 추가가 필요한지 알 수 있음) 

ex)
"mappings": {
        "properties": {
            "content": {
                "type": "text"
            },
            "content_vector": {
                "type": "dense_vector",
                "dims": 512
            }
        }
    }

### Alternatives considered
- Weaviate, Milvus, Vespa, Vald, Chroma 등 선택지가 있었지만, ElasticSearch가 벡엔드에서 DB로 매우 광범위하게 쓰이고 Kibana와의 시각적 연계도 잘되어 있으므로 선택함
- pinecone도 고려 대상이었으나, SaaS인 관계로 벡터 DB를 직접 구축해보자는 취지에 맞지 않아 선택하지 않음
- 위와 마찬가지로 클라우드를 사용하면 제공되는 벡터 DB를 편하게 사용할 수 있지만, SaaS이기도 하고 유료인 관계로 고려하지 않음 

### Cross-cutting concerns
원한다면 벡터 DB에 데이터 저장 시 암호화 고려 가능 
(암호화를 구현해본 적이 없어서 자세한 건 추가 조사가 필요함)
