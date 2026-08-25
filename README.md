# AI-200 Azure AI Cloud Developer Associate

# 2. Main Hands-On Project

## Project: Semantic Document Search Backend

You will gradually build an application with this conceptual architecture:

```text
                         ┌── Azure Cosmos DB
                         │
User → Python API ───────┼── PostgreSQL + pgvector
        │                │
        │                └── Azure Managed Redis
        │
        ├── Service Bus → Background Worker
        │
        └── Event Grid → Azure Function

Application Image
      ↓
     ACR
      ↓
 ┌────┼─────────────┐
 │    │             │
App  Container     AKS
Svc    Apps

Secrets → Key Vault
Configuration → App Configuration

Application
     ↓
OpenTelemetry
     ↓
Application Insights / Azure Monitor
     ↓
KQL
```

You do **not** need to run all components at once.

The objective is to deploy, test, and understand each component so that service-selection questions become intuitive.

---


## 2.1 Technical Design Document — AI-200 KnowledgeHub Master Project

### 2.1.1 Purpose

This section converts the earlier **Semantic Document Search Backend** into a complete master project that can be built throughout the AI-200 study plan. Every major Azure service is included because it solves a specific architectural requirement, not simply to maximize the number of Azure products used.

The project is intended to teach the complete application lifecycle:

```text
Requirement
   ↓
Architecture
   ↓
Python/FastAPI implementation
   ↓
Containerization
   ↓
Azure deployment
   ↓
Security and configuration
   ↓
Observability
   ↓
Troubleshooting
   ↓
CI/CD
```

The project should be implemented incrementally. Each new version extends a system that is already working.

---

### 2.1.2 Project Name

# AI-200 KnowledgeHub

**Full name:** AI-200 KnowledgeHub — Cloud-Native Semantic Document Search and Processing Platform

---

### 2.1.3 Problem Statement

An organization maintains a growing collection of technical documents, operational notes, engineering procedures, design documents, and knowledge articles.

Traditional keyword search becomes increasingly ineffective because users often ask questions using different words from the source documents.

Example:

```text
Document:
"Azure Container Apps can automatically scale replicas from event sources."

User query:
"Which Azure service can increase workers when a queue grows?"
```

A keyword-based search may miss the relationship, while vector similarity can retrieve the relevant passage.

The organization needs a backend platform that can:

1. accept new documents;
2. process them asynchronously;
3. divide documents into semantic chunks;
4. generate vector embeddings;
5. store relational and vector data;
6. perform semantic retrieval;
7. apply metadata filters;
8. cache repeated or semantically similar searches;
9. scale processing workers according to queue backlog;
10. publish domain events when processing completes;
11. maintain operational and audit state;
12. externalize configuration;
13. protect secrets and credentials;
14. trace requests across multiple services;
15. support containerized deployment;
16. support basic CI/CD through Azure DevOps.

This one business problem provides a natural reason to use the services in the AI-200 roadmap.

---

## 2.2 Project Goals and Non-Goals

### Goals

The completed system should demonstrate:

- Python FastAPI REST services;
- Docker-based packaging;
- Azure Container Registry image storage;
- one ACR Tasks cloud build;
- App Service container hosting;
- Azure Container Apps hosting and revisions;
- KEDA event-driven scaling;
- AKS deployment and troubleshooting;
- PostgreSQL relational persistence;
- pgvector semantic retrieval;
- Cosmos DB NoSQL and vector capabilities;
- Cosmos DB change-feed concepts;
- Azure Managed Redis caching and vector search;
- Service Bus durable messaging;
- Event Grid domain-event routing;
- Azure Functions event handling;
- Key Vault secret management;
- App Configuration externalized settings;
- managed identity and RBAC;
- OpenTelemetry distributed tracing;
- Application Insights / Azure Monitor telemetry;
- KQL-based diagnostics;
- Azure DevOps Repos and Pipelines;
- basic CI/CD deployment.

### Non-goals

The first implementation deliberately excludes:

- sophisticated front-end development;
- production-grade multi-tenancy;
- enterprise billing;
- advanced prompt engineering;
- agent orchestration;
- multi-agent systems;
- model fine-tuning;
- speech or vision services;
- enterprise-scale Kubernetes platform engineering;
- complex multi-region disaster recovery.

These can be added later, but they are not necessary for AI-200 preparation.

---

## 2.3 Business Requirements

### BR-01 — Document ingestion

Users must be able to submit a document through a REST endpoint.

```text
POST /documents
```

Example:

```json
{
  "title": "Introduction to Azure Container Apps",
  "category": "azure",
  "department": "cloud",
  "content": "Azure Container Apps provides a managed container environment..."
}
```

The API must return quickly and must not perform the complete embedding workflow before returning.

Expected response:

```json
{
  "document_id": 152,
  "status": "processing"
}
```

Recommended HTTP status:

```text
202 Accepted
```

This immediately introduces an asynchronous processing requirement.

---

### BR-02 — Durable background processing

After storing the document record, the API must send a command to Azure Service Bus.

Queue:

```text
document-processing
```

Message:

```json
{
  "schema_version": "1.0",
  "message_type": "PROCESS_DOCUMENT",
  "document_id": 152,
  "correlation_id": "f14ac8e9-...",
  "requested_at": "2026-08-23T15:45:00Z"
}
```

The background worker must process the message independently from the API request.

---

### BR-03 — Document processing

The ingestion worker must perform:

```text
receive message
    ↓
load document
    ↓
clean text
    ↓
chunk text
    ↓
generate embeddings
    ↓
store vectors
    ↓
update document status
    ↓
publish completion event
```

Initial embedding generation can use a local Python model such as `sentence-transformers` so that the project does not require a paid model endpoint.

---

### BR-04 — Retry and poison-message handling

The worker must exercise:

```text
PeekLock
Complete
Abandon
Retry
Delivery Count
Dead-Letter Queue
```

Transient failures should be retried.

Permanent failures should become observable and, when appropriate, reach the DLQ.

---

### BR-05 — Event-driven scaling

The processing workload is bursty.

When there are no messages:

```text
worker replicas = 0
```

When backlog increases:

```text
Service Bus backlog
       ↓
     KEDA
       ↓
worker replicas increase
```

Initial learning configuration:

```text
minimum replicas = 0
maximum replicas = 5
```

---

### BR-06 — Semantic search

Expose:

```text
POST /search
```

Example request:

```json
{
  "query": "How does event-driven scaling work?",
  "category": "azure",
  "top_k": 5
}
```

Processing:

```text
query
 ↓
embedding
 ↓
semantic cache
 ↓ miss
vector backend
 ↓
metadata filter
 ↓
Top-K results
```

---

### BR-07 — Multiple vector backends

The project must support two vector-search implementations:

```text
PostgreSQL + pgvector
Cosmos DB vector search
```

App Configuration controls the active implementation:

```text
Search:Backend = postgres
```

or:

```text
Search:Backend = cosmos
```

The objective is to compare real architectural alternatives without rewriting the API.

---

### BR-08 — Low-latency caching

Azure Managed Redis must provide:

- cache-aside behavior;
- TTL;
- expiration;
- invalidation;
- optional semantic caching;
- optional vector search.

---

### BR-09 — Domain events

After processing succeeds, publish:

```text
DocumentIndexed
```

After a permanent processing failure, publish:

```text
DocumentProcessingFailed
```

These events communicate facts that already occurred.

---

### BR-10 — Event consumer

An Azure Function subscribes to selected Event Grid events.

Example:

```text
DocumentIndexed
      ↓
Event Grid
      ↓
Azure Function
      ↓
Cosmos operational/audit record
```

---

### BR-11 — Administrative API

Create a separate admin component with endpoints such as:

```text
GET  /admin/documents
GET  /admin/documents/{id}
GET  /admin/jobs
GET  /admin/errors
GET  /admin/config
POST /admin/reindex/{id}
```

Deploy this component to App Service.

This gives App Service a legitimate role instead of duplicating the Container Apps workload.

---

### BR-12 — Kubernetes workload

Create a `vector-benchmark` or `reindex` component that can:

- execute many vector searches;
- compare pgvector and Cosmos search;
- reindex selected documents;
- generate benchmark output.

Deploy this workload to AKS.

This provides a credible reason to learn Kubernetes Deployments, Jobs, ConfigMaps, Secrets, probes, replicas, logs, and events.

---

### BR-13 — External configuration

Move non-secret settings to Azure App Configuration.

Suggested keys:

```text
Search:Backend
Search:TopK
Features:SemanticCache
Features:CosmosVectorSearch
Worker:ChunkSize
Worker:ChunkOverlap
Worker:MaxAttempts
Telemetry:Enabled
```

---

### BR-14 — Secret management

Sensitive values must not be committed to Git.

Candidate secrets:

```text
PostgreSQL password
Redis credential
optional external model API key
```

Store these in Azure Key Vault when a true secret is required.

---

### BR-15 — Azure-native authentication

Use managed identity wherever practical.

Target relationships include:

```text
Container App → Key Vault
Container App → App Configuration
Container App → Service Bus
Container App → Cosmos DB
App Service → Key Vault
Function → Cosmos DB
AKS workload → Azure resources
```

The architectural principle is:

```text
Prefer workload identity over stored credentials.
```

---

### BR-16 — Distributed observability

Every important request path must produce traces.

Example:

```text
Trace: POST /search

├── read_configuration
├── create_query_embedding
├── redis_semantic_cache_lookup
├── postgres_vector_search
├── metadata_filter
└── redis_cache_write
```

---

### BR-17 — CI/CD

Azure DevOps must automate:

```text
source control
  ↓
tests
  ↓
Docker build
  ↓
image tag
  ↓
ACR push
  ↓
deployment
```

The first automated deployment target should be Azure Container Apps.

---

## 2.4 Non-Functional Requirements

### NFR-01 — Responsiveness

Document upload must not wait for embedding generation.

Long-running processing is asynchronous.

### NFR-02 — Reliability

Work must not disappear silently.

Failures should be discoverable through:

```text
message retry
DLQ
worker logs
application telemetry
correlation ID
```

### NFR-03 — Scalability

Workers must scale horizontally from queue backlog and support scale-to-zero.

### NFR-04 — Security

- no real secrets in source control;
- least-privilege permissions;
- Key Vault for secrets;
- App Configuration for non-secret settings;
- managed identity where possible.

### NFR-05 — Observability

The system should answer:

```text
What failed?
Where did it fail?
How long did each dependency take?
Which request/document/message was affected?
```

### NFR-06 — Maintainability

Use a clear project structure and isolate shared concerns.

### NFR-07 — Cost control

Use local containers/emulators for repeated development and create paid Azure resources only for focused cloud labs.

---

## 2.5 Final Logical Architecture

```text
                                      ┌──────────────────────┐
                                      │        USER          │
                                      └──────────┬───────────┘
                                                 │
                                                 ▼
                                  ┌───────────────────────────┐
                                  │ SEARCH / INGEST API       │
                                  │ Python FastAPI            │
                                  │ Azure Container Apps      │
                                  └───────────┬───────────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    │                         │                         │
                    ▼                         ▼                         ▼
        PostgreSQL + pgvector       Azure Managed Redis        Service Bus Queue
        relational + vectors         cache / vectors           document-processing
                    │                         │                         │
                    │                         │                         ▼
                    │                         │                   KEDA scale rule
                    │                         │                         │
                    │                         │                         ▼
                    │                         │               ┌────────────────────┐
                    │                         │               │ Ingestion Worker   │
                    │                         │               │ Python             │
                    │                         │               │ Container Apps     │
                    │                         │               └─────────┬──────────┘
                    │                         │                         │
                    │                         │                 clean/chunk/embed
                    │                         │                         │
                    │                         │                ┌────────┴────────┐
                    │                         │                ▼                 ▼
                    │                         │       PostgreSQL/pgvector    Cosmos DB
                    │                         │
                    │                         └──────── semantic cache
                    │
                    └────────────────── primary search backend


                                       Worker publishes event
                                               │
                                               ▼
                                          Event Grid
                                               │
                                               ▼
                                        Azure Function
                                               │
                                               ▼
                                          Cosmos DB
                                    operational / audit state


       ┌────────────────────────┐               ┌────────────────────────────┐
       │ Admin API              │               │ Vector Benchmark / Reindex │
       │ FastAPI                │               │ Python                     │
       │ App Service            │               │ AKS Deployment / Job       │
       └────────────────────────┘               └────────────────────────────┘


Configuration ───────────────────────────────► Azure App Configuration
Secrets ─────────────────────────────────────► Azure Key Vault
Authentication ───────────────────────────────► Managed Identity / Azure RBAC

All services
    │
    ▼
OpenTelemetry
    │
    ▼
Application Insights / Azure Monitor
    │
    ▼
KQL


Source code
    │
    ▼
Azure DevOps Repos
    │
    ▼
Azure Pipelines
    │
    ├── test
    ├── Docker build
    ├── version/tag
    ▼
Azure Container Registry
    │
    ├── Container Apps
    ├── App Service
    └── AKS
```

---

## 2.6 Service-by-Service Technical Design

### 2.6.1 Python + FastAPI

**Summary:** FastAPI is the primary Python web framework.

**Requirement solved:** REST APIs, request validation, JSON contracts, health endpoints, administration endpoints, and simple asynchronous Python integration.

**Project usage:**

```text
search-api
admin-api
optional ingestion-api
```

**Why selected:** It is lightweight and lets the project concentrate on Azure SDKs, messaging, data access, caching, and observability rather than framework ceremony.

**Hands-on learning:**

- Pydantic models;
- async endpoints;
- dependency injection;
- exception handling;
- structured logging;
- health endpoints;
- configuration loading.

---

### 2.6.2 Docker

**Summary:** Docker packages each service and its dependencies into a reproducible image.

**Requirement solved:** The same application artifact should run locally and on App Service, Container Apps, and AKS.

```text
Source
  ↓
Dockerfile
  ↓
Image
  ↓
Container
```

**Failure labs:** wrong `CMD`, missing package, wrong port, invalid environment variable.

---

### 2.6.3 Azure Container Registry (ACR)

**Summary:** Private registry for versioned container images.

**Requirement solved:** Azure compute services need a centralized, authenticated image source.

**Repositories:**

```text
knowledgehub/search-api
knowledgehub/ingestion-worker
knowledgehub/admin-api
knowledgehub/vector-benchmark
```

**Tag strategy:**

```text
search-api:105
search-api:commit-a4c7f2d
```

Do not depend only on `latest`.

---

### 2.6.4 ACR Tasks

**Summary:** Azure-native cloud-side container build capability.

**Requirement solved:** Provides hands-on experience with building an image inside Azure.

```text
source
  ↓
ACR Task
  ↓
cloud build
  ↓
ACR
```

Later compare this with an Azure Pipelines build agent.

Use it as a focused lab; Azure DevOps becomes the primary final CI/CD path.

---

### 2.6.5 Azure App Service

**Summary:** Managed web-app hosting.

**Project workload:** `admin-api`.

**Requirement solved:** The administration API needs simple managed web hosting but does not require Kubernetes or event-driven worker scaling.

**Why this role matters:** App Service, Container Apps, and AKS are not forced to host the same workload. Each service demonstrates a credible hosting scenario.

**Learning:** container startup, application settings, logs, ACR integration, managed identity.

---

### 2.6.6 Azure Container Apps

**Summary:** Managed container platform for APIs, microservices, revisions, and autoscaling.

**Project workloads:**

```text
search-api
ingestion-api
ingestion-worker
```

**Requirement solved:** Managed container deployment with ingress, revisions, scale-to-zero, and KEDA.

**Revision exercise:**

```text
90% traffic → revision v1
10% traffic → revision v2
```

Then:

```text
100% → revision v2
```

**Important:**

```text
Revision = application/configuration version
Replica  = running instance
```

---

### 2.6.7 KEDA

**Summary:** Event-driven autoscaling.

**Requirement solved:** The ingestion worker should consume minimal compute when idle and scale when Service Bus backlog grows.

```text
Service Bus backlog
       ↓
     KEDA
       ↓
Container App worker replicas
```

**Hands-on proof:** observe replicas at zero, enqueue many messages, watch replicas increase, then observe scale-down.

---

### 2.6.8 Azure Kubernetes Service (AKS)

**Summary:** Managed Kubernetes.

**Project workload:** `vector-benchmark` / reindex workload.

**Requirement solved:** A batch or benchmarking workload provides a realistic reason to learn Kubernetes Deployments, Jobs, ConfigMaps, Secrets, Services, probes, replicas, logs, and events.

**Failure labs:**

```text
ImagePullBackOff
CrashLoopBackOff
wrong service port
bad environment variable
failed readiness probe
```

The entire system is intentionally not moved to AKS because that would add complexity without improving learning for every component.

---

### 2.6.9 Azure Database for PostgreSQL

**Summary:** Managed relational database.

**Project role:** Primary system of record.

**Requirement solved:** Documents, processing jobs, and search history have relational structure and benefit from SQL, constraints, transactions, and indexes.

Suggested tables:

```text
documents
document_chunks
processing_jobs
search_history
```

---

### 2.6.10 pgvector

**Summary:** PostgreSQL extension for vector storage and similarity search.

**Requirement solved:** Users need semantic retrieval rather than only keyword search.

```text
document chunk
    ↓
embedding
    ↓
vector column
    ↓
similarity search
```

**Hands-on scope:** exact search, ANN concepts, HNSW, IVFFlat, DiskANN concept, metadata filtering, `EXPLAIN ANALYZE`, connection pooling.

---

### 2.6.11 Azure Cosmos DB

**Summary:** Distributed NoSQL database.

**Project roles:**

1. denormalized operational/audit state;
2. alternate vector-search backend;
3. change-feed learning.

**Requirement solved:** Provides a NoSQL implementation and an alternative vector architecture for comparison with PostgreSQL.

Example operational item:

```json
{
  "id": "processing-152",
  "documentId": 152,
  "status": "indexed",
  "chunks": 18,
  "processingTimeMs": 2830,
  "correlationId": "f14ac8e9-..."
}
```

---

### 2.6.12 Cosmos DB Change Feed

**Summary:** Change stream over Cosmos item updates.

**Requirement solved:** Provides hands-on experience with change-driven processing originating from database updates.

Example learning flow:

```text
Cosmos item changes
       ↓
change feed
       ↓
reader/processor
       ↓
metric/read-model/test action
```

**Architectural lesson:** distinguish a database change stream from an application domain event published through Event Grid.

---

### 2.6.13 Azure Managed Redis

**Summary:** Low-latency in-memory data platform.

**Project roles:** response cache, TTL experiment, invalidation, semantic cache, optional vector retrieval.

**Requirement solved:** Avoid unnecessary vector-database queries for repeated searches.

```text
query
 ↓
Redis
 ├─ hit → return
 └─ miss
     ↓
 vector backend
     ↓
 cache result
     ↓
 return
```

Advanced version: store query embeddings so semantically similar queries can reuse cached results.

---

### 2.6.14 Azure Service Bus

**Summary:** Durable enterprise messaging.

**Project role:** `document-processing` work queue.

**Requirement solved:** Document processing must be asynchronous, retryable, durable, and consumable by multiple worker replicas.

**Behaviors to learn:** queue, topic/subscription extension, PeekLock, Complete, Abandon, Retry, DLQ, correlation IDs, competing consumers.

**Mental model:**

```text
Service Bus command:
"Please process this document."
```

---

### 2.6.15 Azure Event Grid

**Summary:** Event-routing service.

**Project events:**

```text
DocumentIndexed
DocumentProcessingFailed
DocumentDeleted
DocumentReindexed
```

**Requirement solved:** Independent consumers may need to react to something that has already happened.

**Mental model:**

```text
Event Grid event:
"This thing happened."
```

This boundary between Service Bus and Event Grid is a central architecture lesson.

---

### 2.6.16 Azure Functions

**Summary:** Serverless event-driven compute.

**Project role:** Consume Event Grid events and write/update operational state.

**Requirement solved:** The handler is short-lived and event-triggered; a continuously running process would be unnecessary.

---

### 2.6.17 Azure Key Vault

**Summary:** Secure storage for secrets, keys, and certificates.

**Requirement solved:** Sensitive data must not be hard-coded, committed to Git, or stored as ordinary configuration.

Examples:

```text
PostgreSQL password
Redis credential
optional model API key
```

**Learning extension:** rotate a secret and verify the application can retrieve the new version.

---

### 2.6.18 Azure App Configuration

**Summary:** Centralized non-secret application configuration.

**Requirement solved:** Runtime behavior should change without rebuilding Docker images.

Example:

```text
Search:Backend = postgres
```

change to:

```text
Search:Backend = cosmos
```

without changing source code.

---

### 2.6.19 Managed Identity

**Summary:** Azure-managed workload identity.

**Requirement solved:** Reduce credential storage and use Azure RBAC.

```text
Azure workload
    ↓
Managed Identity
    ↓
Azure resource
```

**Learning:** authentication vs authorization, role assignment, least privilege.

---

### 2.6.20 OpenTelemetry

**Summary:** Open standard for traces, metrics, and logs.

**Requirement solved:** Distributed request latency and failures must be visible across service boundaries.

Example trace:

```text
POST /search
│
├── create_embedding
├── redis_lookup
├── pgvector_search
├── metadata_filter
└── redis_write
```

---

### 2.6.21 Application Insights / Azure Monitor

**Summary:** Azure observability platform.

**Requirement solved:** Central visibility for requests, dependencies, exceptions, traces, and metrics.

The system should be diagnosable without scattering ad-hoc `print()` statements throughout production code.

---

### 2.6.22 KQL

**Summary:** Query language for Azure telemetry.

**Requirement solved:** Analyze errors and performance.

Questions the project should answer:

```text
Which endpoint has the highest failure rate?
Which searches exceed 1 second?
Which dependency causes the most latency?
How many worker jobs failed in the last hour?
What percentage of searches were cache hits?
```

---

### 2.6.23 Azure DevOps Repos

**Summary:** Git hosting in Azure DevOps.

**Requirement solved:** Central source control and branch-based development.

Suggested simple branch model:

```text
main
develop
feature/*
```

---

### 2.6.24 Azure Pipelines

**Summary:** CI/CD automation.

**Requirement solved:** Automate testing, building, image publishing, and deployment.

Final flow:

```text
commit
  ↓
tests
  ↓
Docker build
  ↓
image tag
  ↓
ACR push
  ↓
Container Apps deployment
```

AKS deployment can be added as an advanced extension.

---

## 2.7 Service-to-Requirement Traceability Matrix

| Service / Technology | Requirement Solved | Project Role |
|---|---|---|
| Python + FastAPI | REST/backend application | Search, ingestion, admin APIs |
| Docker | Reproducible packaging | Same artifact across environments |
| ACR | Private image storage | Versioned image repository |
| ACR Tasks | Azure-native build | Focused cloud-build exercise |
| App Service | Managed web hosting | Admin API |
| Container Apps | Managed microservices | Search API and worker |
| KEDA | Event-driven scaling | Scale worker from queue backlog |
| AKS | Kubernetes operations | Benchmark/reindex workload |
| PostgreSQL | Relational persistence | System of record |
| pgvector | Semantic search | Primary vector backend |
| Cosmos DB | NoSQL + vectors | Operational state + alternate search |
| Cosmos Change Feed | Database change processing | Change-stream lab |
| Managed Redis | Low-latency cache | Cache + semantic cache |
| Service Bus | Durable commands | Document-processing queue |
| Event Grid | Domain-event routing | Publish processing events |
| Azure Functions | Event handler | Consume Event Grid events |
| Key Vault | Secret storage | Protect credentials |
| App Configuration | Runtime settings | Backend/feature configuration |
| Managed Identity | Azure authentication | Minimize embedded credentials |
| OpenTelemetry | Instrumentation | Distributed tracing |
| Application Insights | App telemetry | Requests/dependencies/exceptions |
| Azure Monitor | Operational monitoring | Central visibility |
| KQL | Telemetry analysis | Diagnostics and performance |
| Azure DevOps Repos | Source control | Git workflow |
| Azure Pipelines | CI/CD | Test/build/push/deploy |

---

## 2.8 Data Design

### 2.8.1 PostgreSQL — `documents`

```sql
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT,
    department TEXT,
    content TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

Statuses:

```text
received
queued
processing
indexed
failed
```

---

### 2.8.2 PostgreSQL — `document_chunks`

```sql
CREATE TABLE document_chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT NOT NULL,
    chunk_number INT NOT NULL,
    chunk_text TEXT NOT NULL,
    category TEXT,
    department TEXT,
    embedding VECTOR(...),
    created_at TIMESTAMP NOT NULL
);
```

The vector dimension depends on the selected embedding model.

---

### 2.8.3 PostgreSQL — `processing_jobs`

Suggested fields:

```text
id
document_id
correlation_id
status
attempt_count
started_at
completed_at
error_message
```

---

### 2.8.4 PostgreSQL — `search_history`

Suggested fields:

```text
id
query_text
backend
cache_hit
top_k
duration_ms
created_at
```

This table is optional but useful for performance experiments.

---

### 2.8.5 Cosmos operational item

```json
{
  "id": "processing-152",
  "documentId": 152,
  "partitionKey": "azure",
  "status": "indexed",
  "chunks": 18,
  "processingTimeMs": 2830,
  "correlationId": "f14ac8e9-...",
  "timestamp": "2026-08-23T15:47:10Z"
}
```

---

### 2.8.6 Redis cache key

Exact-cache form:

```text
search:v1:<hash-of-normalized-query-and-filters>
```

Cached payload:

```json
{
  "query": "how does keda work",
  "backend": "postgres",
  "results": [],
  "created_at": "..."
}
```

TTL should be configurable.

---

## 2.9 API Contracts

### Health

```text
GET /health
```

```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Create document

```text
POST /documents
```

```json
{
  "title": "KEDA Overview",
  "category": "azure",
  "department": "cloud",
  "content": "KEDA enables event-driven autoscaling..."
}
```

Response:

```json
{
  "document_id": 152,
  "status": "processing"
}
```

### Document status

```text
GET /documents/{document_id}
```

```json
{
  "document_id": 152,
  "status": "indexed",
  "chunk_count": 18
}
```

### Semantic search

```text
POST /search
```

```json
{
  "query": "Which service scales workers from queue backlog?",
  "category": "azure",
  "top_k": 5
}
```

Response:

```json
{
  "query": "Which service scales workers from queue backlog?",
  "backend": "postgres",
  "cache_hit": false,
  "results": [
    {
      "document_id": 152,
      "chunk_id": 4,
      "score": 0.91,
      "text": "KEDA can scale workloads based on event sources..."
    }
  ]
}
```

### Reindex

```text
POST /admin/reindex/{document_id}
```

This should enqueue work rather than performing reindexing inside the HTTP request.

---

## 2.10 Messaging and Event Contracts

### Service Bus command

```json
{
  "schema_version": "1.0",
  "message_type": "PROCESS_DOCUMENT",
  "document_id": 152,
  "correlation_id": "f14ac8e9-...",
  "requested_at": "2026-08-23T15:45:00Z"
}
```

### `DocumentIndexed` event

```json
{
  "eventType": "DocumentIndexed",
  "subject": "documents/152",
  "data": {
    "documentId": 152,
    "chunkCount": 18,
    "processingTimeMs": 2830
  }
}
```

### `DocumentProcessingFailed` event

```json
{
  "eventType": "DocumentProcessingFailed",
  "subject": "documents/152",
  "data": {
    "documentId": 152,
    "reason": "embedding generation failed"
  }
}
```

### Core distinction

```text
Service Bus command:
"Process document 152."

Event Grid event:
"Document 152 has been indexed."
```

---

## 2.11 Search Processing Design

```text
1. Receive request
2. Validate request
3. Read configuration
4. Generate query embedding
5. Check Redis semantic cache
6. If hit → return cached result
7. If miss → select backend
8. Search pgvector or Cosmos
9. Apply metadata filters
10. Return Top-K results
11. Cache result
12. Record telemetry
```

Backend-selection pseudo-code:

```python
if search_backend == "postgres":
    results = postgres_vector_search(...)
elif search_backend == "cosmos":
    results = cosmos_vector_search(...)
else:
    raise ConfigurationError("Unsupported search backend")
```

This creates a direct, practical App Configuration exercise.

---

## 2.12 Local Development Architecture

Build the system locally before deploying Azure components.

```text
┌──────────────────────────────────────────────────────┐
│                 LOCAL DEVELOPMENT                    │
│                                                      │
│ FastAPI search-api                                   │
│ FastAPI admin-api                                    │
│ Python ingestion-worker                              │
│ PostgreSQL + pgvector                                │
│ Redis / Redis Stack                                  │
│ Service Bus Emulator                                 │
│ Cosmos Emulator where appropriate                    │
│ Azure Functions Core Tools                           │
│ OpenTelemetry SDK                                    │
│                                                      │
└──────────────────────────────────────────────────────┘
```

Suggested Docker Compose services:

```text
postgres
redis
search-api
ingestion-worker
admin-api
```

Use Azure only when the cloud-specific behavior itself is the learning objective.

---

## 2.13 Recommended Repository Structure

```text
ai200-knowledgehub/
│
├── services/
│   ├── search-api/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   ├── services/
│   │   │   ├── repositories/
│   │   │   ├── models/
│   │   │   └── main.py
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── ingestion-worker/
│   │   ├── app/
│   │   │   ├── consumers/
│   │   │   ├── chunking/
│   │   │   ├── embeddings/
│   │   │   ├── repositories/
│   │   │   └── main.py
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── admin-api/
│   │   ├── app/
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── vector-benchmark/
│       ├── app/
│       ├── tests/
│       ├── requirements.txt
│       └── Dockerfile
│
├── functions/
│   └── document-event-handler/
│
├── shared/
│   ├── config/
│   ├── telemetry/
│   ├── models/
│   ├── logging/
│   └── azure_clients/
│
├── database/
│   ├── migrations/
│   └── seed/
│
├── infrastructure/
│   ├── bicep/
│   ├── containerapps/
│   ├── appservice/
│   └── kubernetes/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── configmap.yaml
│       └── job.yaml
│
├── pipelines/
│   ├── ci.yml
│   ├── deploy-containerapps.yml
│   └── deploy-aks.yml
│
├── docker-compose.yml
├── .env.example
├── README.md
└── architecture.md
```

---

## 2.14 Security Design

### Local development

Use `.env` only for local development.

Do not commit it.

Commit `.env.example` containing placeholders.

### Azure workloads

Preferred authentication flow:

```text
Application
    ↓
DefaultAzureCredential
    ↓
Managed Identity
    ↓
Azure RBAC
    ↓
Azure resource
```

### Least privilege

Example permissions:

```text
search-api
  → read App Configuration
  → read required Key Vault secrets
  → query PostgreSQL/Cosmos
  → use Redis

ingestion-worker
  → receive Service Bus messages
  → write PostgreSQL vectors
  → write Cosmos data
  → publish events

Function
  → receive event trigger
  → write operational state
```

---

## 2.15 Observability Design

### Correlation ID

Generate a correlation ID when a document request begins and propagate it through:

```text
HTTP request
→ Service Bus message
→ worker
→ Event Grid event
→ Function
→ telemetry
```

### Search trace

```text
POST /search
│
├── read_app_configuration
├── create_query_embedding
├── redis_cache_lookup
├── postgres_vector_search
├── metadata_filter
├── redis_cache_write
└── serialize_response
```

### Ingestion trace

```text
PROCESS_DOCUMENT
│
├── load_document
├── clean_text
├── chunk_text
├── generate_embeddings
├── write_pgvector
├── write_cosmos
└── publish_event
```

### Suggested custom metrics

```text
knowledgehub.search.duration_ms
knowledgehub.search.cache_hit
knowledgehub.search.result_count
knowledgehub.worker.processing_ms
knowledgehub.worker.chunk_count
knowledgehub.worker.failure_count
knowledgehub.vector.backend
```

### KQL questions to answer

```text
Which search requests failed in the last hour?
Which dependency has the highest average latency?
Which vector backend is used most often?
What percentage of searches are cache hits?
Which document-processing jobs failed?
Which endpoint has the highest P95 latency?
```

---

## 2.16 Failure and Troubleshooting Design

### Scenario 1 — Bad container image

Investigate:

```text
image tag
ACR repository
Container Apps revision status
AKS pod status
deployment logs
```

### Scenario 2 — PostgreSQL unavailable

Observe:

```text
application exception
OpenTelemetry dependency span
connection timeout
request latency
```

### Scenario 3 — Redis unavailable

Desired behavior:

```text
cache failure
  ↓
log/trace failure
  ↓
continue to primary vector backend
```

This teaches graceful degradation.

### Scenario 4 — Poison Service Bus message

Observe:

```text
retries
increasing delivery count
worker logs
DLQ
```

### Scenario 5 — Wrong AKS service port

Use:

```bash
kubectl get services
kubectl describe
kubectl logs
kubectl get events
```

### Scenario 6 — Key Vault authorization failure

Separate:

```text
authentication
```

from:

```text
authorization
```

Check identity, RBAC, vault permissions, and secret name.

### Scenario 7 — Bad configuration

Set:

```text
Search:Backend = invalid-backend
```

The application should produce a clear configuration error.

---

## 2.17 Azure DevOps CI/CD Design

### Source control

Use Azure DevOps Repos.

Suggested lightweight branch model:

```text
main
develop
feature/*
```

### Continuous Integration

Trigger on pull request or commit to `develop`.

```text
Checkout
   ↓
Python setup
   ↓
Install dependencies
   ↓
Lint
   ↓
Unit tests
   ↓
Docker build
   ↓
CI result
```

The first CI pipeline should not deploy. Its job is simply to answer:

```text
Does this change build and pass tests?
```

### Image publishing

After tests pass:

```text
Docker build
   ↓
Tag image
   ↓
Push to ACR
```

Suggested tags:

```text
$(Build.BuildId)
commit SHA
```

Example:

```text
search-api:105
search-api:a4c7f2d
```

### Container Apps deployment

Primary CD flow:

```text
Commit to main
      ↓
CI
      ↓
Docker build
      ↓
ACR
      ↓
Container Apps
      ↓
new revision
```

Use this to learn revision creation, validation, traffic movement, and rollback thinking.

### App Service deployment

For `admin-api`:

```text
build image
  ↓
ACR
  ↓
App Service
```

### AKS deployment

Advanced extension:

```text
build vector-benchmark
      ↓
ACR
      ↓
update manifest/image
      ↓
deploy to AKS
```

### Environments

After basic CI/CD works:

```text
develop → DEV
main    → PROD
```

Optionally add manual approval before PROD.

---

## 2.18 Infrastructure-as-Code Recommendation

Infrastructure-as-Code is useful but should not hide the Azure concepts during first exposure.

Recommended tool:

```text
Bicep
```

Add IaC gradually after manual deployment works.

Potential modules:

```text
ACR
Container Apps environment
Container Apps
Service Bus
App Configuration
Key Vault
Application Insights
```

Recommended learning order:

```text
manual deployment
   ↓
understand service
   ↓
automate with Bicep
```

---

## 2.19 Cost-Aware Project Strategy

### Keep local for repeated development

```text
FastAPI
Docker
PostgreSQL + pgvector
Redis
Service Bus Emulator
Functions Core Tools
local Kubernetes
OpenTelemetry
```

### Use real Azure when cloud behavior matters

```text
ACR
App Service
Container Apps
KEDA
Cosmos DB
Event Grid
Functions
Key Vault
App Configuration
Application Insights
```

### Create only for focused labs when they can cost money

```text
AKS
Azure Managed Redis
Azure PostgreSQL when no free allowance exists
ACR Tasks build compute
```

Rule:

```text
Create → Learn → Record observations → Delete
```

---

## 2.20 Project Implementation Versions

### Version 1 — Local FastAPI foundation

Build:

```text
search-api
health endpoint
document endpoint
basic logging
```

**Goal:** understand FastAPI and the basic API structure.

### Version 2 — PostgreSQL persistence

Add:

```text
documents
processing_jobs
Python database access
```

**Goal:** establish the relational system of record.

### Version 3 — Docker

Containerize the API.

**Goal:** learn reproducible packaging and Docker troubleshooting.

### Version 4 — pgvector

Add:

```text
document_chunks
embeddings
semantic search
metadata filtering
```

**Goal:** implement the first complete vector-search path.

### Version 5 — Redis

Add:

```text
cache-aside
TTL
invalidation
semantic cache
```

**Goal:** learn low-latency caching and vector-capable Redis.

### Version 6 — Service Bus + worker

Refactor:

```text
API
 ↓
Service Bus
 ↓
Worker
```

**Goal:** learn asynchronous and durable processing.

### Version 7 — Local distributed stack

Run API, worker, PostgreSQL, Redis, and messaging together.

**Goal:** understand component boundaries before Azure deployment.

### Version 8 — ACR

Push project images to Azure Container Registry.

**Goal:** learn private image storage and versioning.

### Version 9 — App Service

Deploy `admin-api`.

**Goal:** learn managed web/container hosting.

### Version 10 — Container Apps

Deploy `search-api` and `ingestion-worker`.

**Goal:** learn ingress, revisions, replicas, configuration, and secrets.

### Version 11 — KEDA

Scale the worker from Service Bus backlog.

**Goal:** learn event-driven scale-to-zero.

### Version 12 — Cosmos DB

Add:

```text
operational records
alternate vector backend
change-feed exercise
```

**Goal:** learn NoSQL, vector search, indexing/RU thinking, and change processing.

### Version 13 — Event Grid + Function

Publish `DocumentIndexed` and consume it with an Azure Function.

**Goal:** learn domain events and serverless event handling.

### Version 14 — App Configuration

Move runtime settings outside code.

**Goal:** learn dynamic external configuration.

### Version 15 — Key Vault + Managed Identity

Move secrets to Key Vault and replace credentials with managed identity where possible.

**Goal:** learn Azure security and authorization.

### Version 16 — AKS

Deploy `vector-benchmark`.

**Goal:** learn Kubernetes developer operations and troubleshooting.

### Version 17 — Observability

Add OpenTelemetry, Application Insights, Azure Monitor, and KQL.

**Goal:** trace distributed requests and diagnose failures.

### Version 18 — Azure DevOps CI/CD

Automate:

```text
test
build
tag
push
deploy
```

**Goal:** learn a basic professional delivery workflow.

---

## 2.21 End-to-End Reference Scenario

The completed system should support this complete flow.

### Step 1 — Upload

User calls:

```text
POST /documents
```

### Step 2 — Persist

FastAPI creates a document row in PostgreSQL.

### Step 3 — Enqueue

FastAPI sends `PROCESS_DOCUMENT` to Service Bus.

### Step 4 — Scale

Queue backlog increases and KEDA scales the ingestion worker.

### Step 5 — Process

Worker:

```text
loads document
↓
cleans text
↓
chunks text
↓
generates embeddings
↓
stores pgvector data
↓
stores Cosmos operational/vector data
```

### Step 6 — Publish event

Worker publishes `DocumentIndexed` to Event Grid.

### Step 7 — Function reaction

Azure Function receives the event and writes/updates operational state.

### Step 8 — Search

User calls:

```text
POST /search
```

with:

```text
"What is KEDA?"
```

### Step 9 — Cache lookup

Search API checks Redis semantic cache.

### Step 10 — Vector search

On a cache miss, App Configuration selects the backend.

Example:

```text
Search:Backend = postgres
```

The API performs pgvector search.

### Step 11 — Cache write

The response is stored in Redis.

### Step 12 — Observability

The complete path is visible through OpenTelemetry → Application Insights → KQL.

### Step 13 — Code change

Developer commits a change.

### Step 14 — CI/CD

```text
git push
   ↓
Azure DevOps
   ↓
tests
   ↓
Docker build
   ↓
ACR
   ↓
Container Apps new revision
```

This single scenario ties together nearly every service in the master project.

---

## 2.22 Testing Strategy

### Unit tests

Test:

- request validation;
- chunking logic;
- cache-key generation;
- search-backend selection;
- Service Bus message parsing;
- Event Grid payload creation.

### Integration tests

Test:

```text
API ↔ PostgreSQL
API ↔ Redis
API ↔ Service Bus
worker ↔ PostgreSQL
worker ↔ Cosmos
```

Use local infrastructure when practical.

### Contract tests

Verify required fields in messages and events.

For example, every `PROCESS_DOCUMENT` command must contain:

```text
message_type
document_id
correlation_id
requested_at
```

### Failure tests

Test:

```text
Redis unavailable
PostgreSQL unavailable
invalid queue message
Key Vault access denied
invalid App Configuration
bad image tag
failed AKS readiness
```

### Performance experiments

Use small controlled comparisons:

```text
search without Redis
vs
search with Redis

exact vector search
vs
indexed ANN search

PostgreSQL backend
vs
Cosmos backend
```

The objective is to observe architectural behavior, not to conduct enterprise-scale load testing.

---

## 2.23 Definition of Done

### Application

- [ ] Create documents through FastAPI.
- [ ] Persist documents in PostgreSQL.
- [ ] Queue processing using Service Bus.
- [ ] Process documents asynchronously.
- [ ] Generate and store embeddings.
- [ ] Perform pgvector semantic search.
- [ ] Perform Cosmos vector search.
- [ ] Use metadata filtering.
- [ ] Cache search results in Redis.
- [ ] Demonstrate semantic caching/vector retrieval.
- [ ] Publish Event Grid events.
- [ ] Handle an event with Azure Functions.

### Compute

- [ ] Build Docker images.
- [ ] Push images to ACR.
- [ ] Perform one ACR Task build.
- [ ] Deploy admin API to App Service.
- [ ] Deploy search API to Container Apps.
- [ ] Deploy worker to Container Apps.
- [ ] Demonstrate revisions.
- [ ] Demonstrate KEDA scaling.
- [ ] Deploy benchmark workload to AKS.

### Security and configuration

- [ ] Store secrets in Key Vault.
- [ ] Read runtime settings from App Configuration.
- [ ] Use managed identity for multiple Azure-resource connections.
- [ ] Demonstrate one authorization failure and fix it.

### Observability

- [ ] Instrument search with OpenTelemetry.
- [ ] Instrument worker processing.
- [ ] View distributed traces.
- [ ] Query failures with KQL.
- [ ] Identify one slow dependency using telemetry.

### CI/CD

- [ ] Store code in Azure DevOps Repos.
- [ ] Run unit tests through Azure Pipelines.
- [ ] Build Docker image in a pipeline.
- [ ] Push a versioned image to ACR.
- [ ] Deploy a new Container Apps revision automatically.
- [ ] Optionally deploy an AKS workload through a pipeline.

---

## 2.24 Architectural Learning Outcomes

The project should make these boundaries intuitive:

```text
App Service
vs
Container Apps
vs
AKS
```

```text
Service Bus
vs
Event Grid
```

```text
Queue
vs
Topic
```

```text
PostgreSQL
vs
Cosmos DB
vs
Redis
```

```text
pgvector
vs
Cosmos vector search
vs
Redis vector search
```

```text
Key Vault
vs
App Configuration
```

```text
Secret
vs
Managed Identity
```

```text
Logs
vs
Metrics
vs
Traces
```

```text
Continuous Integration
vs
Continuous Deployment
```

The purpose is to learn these distinctions through implementation rather than memorization.



