# Field Reference for Integration Scripts

Use this document as a quick checklist when deciding what configuration to collect and what data fields to request from Microsoft Agent 365, Microsoft Purview, and Microsoft Entra/Microsoft Graph.

> **Important:** This is a practical cross-service reference, not a promise that every field is returned by every endpoint. SDK versions, API versions, asset types, permissions, and preview features determine availability. Use explicit field selection and validate against the official API schema used by your script.

## 1. Configuration fields

### Runtime

| Environment field | Required | Typical value | Purpose |
|---|---:|---|---|
| `AGENT_NAME` | Yes | `secure-agent` | Stable service/agent name |
| `AGENT_ENV` | Yes | `development`, `test`, `production` | Environment name |
| `LOG_LEVEL` | Yes | `info` | Logging threshold |
| `LOG_FORMAT` | No | `json` | Machine-readable logs |
| `REQUEST_TIMEOUT_MS` | No | `30000` | Default outbound timeout |
| `CORRELATION_HEADER` | No | `x-correlation-id` | Correlation header name |
| `MAX_RETRY_ATTEMPTS` | No | `3` | Bounded transient retries |
| `RETRY_BASE_DELAY_MS` | No | `500` | Retry backoff base |

### Entra and Microsoft Graph

| Environment field | Required | Purpose |
|---|---:|---|
| `ENTRA_TENANT_ID` | Yes | Tenant ID |
| `ENTRA_CLIENT_ID` | Yes | App registration or managed identity client ID |
| `ENTRA_CLIENT_SECRET` | Dev only | Confidential-client secret |
| `ENTRA_CLIENT_CERT_PATH` | Alternative | Certificate credential path |
| `ENTRA_AUTHORITY_HOST` | No | Authority host; normally `https://login.microsoftonline.com` |
| `ENTRA_USE_MANAGED_IDENTITY` | No | Select managed identity auth |
| `GRAPH_BASE_URL` | Yes | Normally `https://graph.microsoft.com/v1.0` |
| `GRAPH_SCOPES` | Yes | Normally `https://graph.microsoft.com/.default` for app-only auth |

### Purview

| Environment field | Required | Purpose |
|---|---:|---|
| `PURVIEW_ENABLED` | No | Enable the adapter |
| `PURVIEW_ENDPOINT` | Yes | Purview account/data-plane endpoint |
| `PURVIEW_API_VERSION` | Yes | Version explicitly tested by the application |
| `PURVIEW_SCOPES` | Yes | Normally `https://purview.azure.net/.default` |
| `PURVIEW_COLLECTION_ID` | No | Default collection boundary |
| `PURVIEW_TIMEOUT_MS` | No | Adapter-specific timeout |
| `PURVIEW_RETRY_MAX` | No | Adapter-specific retry limit |

### Agent 365

| Environment field | Required | Purpose |
|---|---:|---|
| `A365_ENABLED` | No | Enable Agent 365 capabilities |
| `A365_SDK_LANGUAGE` | Yes | `dotnet`, `node`, or `python` when supported by the selected package |
| `A365_SDK_PACKAGE_PREFIX` | Yes | Package family; .NET packages currently use `Microsoft.Agents.A365` |
| `A365_SDK_SOURCE` | Yes | Authoritative package/release source used by update automation |
| `A365_NOTIFICATION_ENABLED` | No | Enable notification integration |
| `A365_OBSERVABILITY_ENABLED` | No | Enable tracing/monitoring integration |
| `A365_TOOLING_ENABLED` | No | Enable development/runtime utilities |

## 2. Common request-control fields

Use these controls in adapter request objects where the target service supports them.

| Normalized field | Graph mapping | Purview mapping | Purpose |
|---|---|---|---|
| `select` | `$select` | Map after response or use endpoint-specific projection | Return only needed fields |
| `filter` | `$filter` | `filter` | Server-side filtering |
| `search` | `$search` | `keywords` | Text/directory search |
| `orderBy` | `$orderby` | `orderby` | Sort results |
| `pageSize` | `$top` | `limit` or `top` | Requested page size |
| `pageToken` | URL from `@odata.nextLink` | `continuationToken`, or `skip` | Continue paging |
| `expand` | `$expand` | `ignoreRelationships=false` / endpoint options | Include relationships |
| `includeCount` | `$count=true` | Facet counts/response totals where supported | Return counts |
| `apiVersion` | URL version (`v1.0` or explicitly approved preview) | `api-version` | Pin API contract |

## 3. Microsoft Entra / Graph fields to pull

### Users (`/users`)

Recommended basic `$select`:

```text
id,displayName,userPrincipalName,mail,accountEnabled,userType,jobTitle,department,companyName,officeLocation,preferredLanguage,createdDateTime
```

Additional fields by use case:

| Category | Fields |
|---|---|
| Identity | `id`, `displayName`, `givenName`, `surname`, `userPrincipalName`, `mail`, `mailNickname`, `proxyAddresses`, `identities`, `onPremisesImmutableId` |
| Account state | `accountEnabled`, `userType`, `creationType`, `createdDateTime`, `deletedDateTime`, `externalUserState`, `externalUserStateChangeDateTime` |
| Organization | `jobTitle`, `department`, `companyName`, `employeeId`, `employeeType`, `employeeHireDate`, `officeLocation`, `manager` relationship |
| Contact | `businessPhones`, `mobilePhone`, `streetAddress`, `city`, `state`, `postalCode`, `country`, `usageLocation` |
| Licensing | `assignedLicenses`, `assignedPlans`, `licenseAssignmentStates` |
| Sync | `onPremisesSyncEnabled`, `onPremisesDomainName`, `onPremisesSamAccountName`, `onPremisesUserPrincipalName`, `onPremisesLastSyncDateTime`, `onPremisesProvisioningErrors` |
| Security-sensitive | `passwordPolicies`, `passwordProfile`, `signInActivity`, `customSecurityAttributes` — request only with an approved use case and required permissions |

Example:

```http
GET /v1.0/users?$select=id,displayName,userPrincipalName,mail,accountEnabled,department,jobTitle
```

### Groups (`/groups`)

```text
id,displayName,description,mail,mailEnabled,mailNickname,securityEnabled,groupTypes,visibility,createdDateTime,renewedDateTime,expirationDateTime,membershipRule,membershipRuleProcessingState,isAssignableToRole
```

Relationships commonly retrieved separately or with supported expansion:

- `members`
- `transitiveMembers`
- `owners`
- `memberOf`
- `transitiveMemberOf`
- `appRoleAssignments`

### Applications (`/applications`)

```text
id,appId,displayName,description,createdDateTime,signInAudience,identifierUris,publisherDomain,verifiedPublisher,api,appRoles,requiredResourceAccess,optionalClaims,web,spa,publicClient,keyCredentials,passwordCredentials,tags,serviceManagementReference
```

Treat `keyCredentials` and `passwordCredentials` as metadata only. Never copy secret material into logs or output files.

### Service principals (`/servicePrincipals`)

```text
id,appId,displayName,description,accountEnabled,servicePrincipalType,signInAudience,appOwnerOrganizationId,appRoleAssignmentRequired,appRoles,oauth2PermissionScopes,servicePrincipalNames,tags,verifiedPublisher,preferredSingleSignOnMode,notificationEmailAddresses,homepage,loginUrl,replyUrls,createdDateTime
```

Relationships/permission data:

- `appRoleAssignments`
- `appRoleAssignedTo`
- `oauth2PermissionGrants`
- `owners`
- `memberOf`
- `transitiveMemberOf`

### App role assignments

```text
id,appRoleId,createdDateTime,principalDisplayName,principalId,principalType,resourceDisplayName,resourceId
```

### Directory roles and role assignments

Useful resources and fields:

| Resource | Fields |
|---|---|
| `directoryRoles` | `id`, `displayName`, `description`, `roleTemplateId` |
| `roleManagement/directory/roleDefinitions` | `id`, `displayName`, `description`, `isBuiltIn`, `isEnabled`, `templateId`, `rolePermissions`, `inheritsPermissionsFrom` |
| `roleManagement/directory/roleAssignments` | `id`, `principalId`, `roleDefinitionId`, `directoryScopeId`, `appScopeId` |
| `roleManagement/directory/roleEligibilityScheduleInstances` | IDs, principal, role definition, scope, start/end dates, assignment type, member type |
| `roleManagement/directory/roleAssignmentScheduleInstances` | IDs, principal, role definition, scope, start/end dates, assignment type, member type |

### Query and synchronization options

- Use `$select` because many Graph properties are not returned by default.
- Follow `@odata.nextLink`; do not construct subsequent page URLs manually.
- Preserve `@odata.deltaLink` when using supported delta endpoints.
- Advanced `$filter`/`$search` combinations can require `ConsistencyLevel: eventual` and `$count=true`.
- Beta-only fields must not be introduced into production scripts without explicit approval and compatibility tests.

## 4. Microsoft Purview fields to pull

### Discovery search request

| Field | Type | Notes |
|---|---|---|
| `keywords` | string | Search terms across searchable fields |
| `filter` | object | Nested `and`, `or`, and endpoint-supported field predicates |
| `limit` | integer | Result limit; obey endpoint maximum |
| `continuationToken` | string | Next page token |
| `orderby` | array | Field/direction objects |
| `facets` | array | Facet name, count, and sort settings |
| `taxonomySetting` | object | Taxonomy behavior where supported |

Common filter/facet concepts include:

```text
id,objectType,entityType,assetType,classification,collectionId,contactId,label,term,fileExtension,systemTime,updateTime
```

Supported names vary by API version and search endpoint; reject unknown fields rather than silently ignoring them.

### Entity lookup request

| Input | Purpose |
|---|---|
| `guid` | Get an entity by globally unique ID |
| `typeName` | Entity type for unique-attribute lookup |
| `attr:qualifiedName` | Common unique attribute selector |
| `minExtInfo` | Request minimal referred-entity data |
| `ignoreRelationships` | Exclude relationship attributes when not needed |

### Core entity response

```text
guid,typeName,status,attributes,relationshipAttributes,businessAttributes,classifications,meanings,labels,contacts,collectionId,customAttributes,createTime,updateTime,createdBy,updatedBy,lastModifiedTS,version,provenanceType,homeId,isIncomplete
```

Recommended normalized asset fields:

| Normalized field | Typical Purview source |
|---|---|
| `id` | `guid` |
| `resourceType` | `typeName` |
| `name` | `attributes.name` |
| `qualifiedName` | `attributes.qualifiedName` |
| `description` | `attributes.description` |
| `owner` | `attributes.owner` or `contacts.Owner` |
| `experts` | `contacts.Expert` |
| `status` | `status` |
| `collectionId` | `collectionId` |
| `classifications` | `classifications` |
| `terms` | `meanings` |
| `labels` | `labels` |
| `createdAt` | `createTime` |
| `updatedAt` | `updateTime` |
| `etag` | `lastModifiedTS` |

### Entity attributes

`attributes` is type-specific. Common examples include:

```text
name,qualifiedName,description,owner,createTime,modifiedTime,dataType,type,schema,columns,table,server,host,port,protocol,path,resourceGroup,subscriptionId,accountName,databaseName,schemaName
```

Do not assume all attributes exist. Preserve unknown fields in a non-logged `raw.attributes` object only when the use case needs forward compatibility.

### Classifications

Common classification fields:

```text
typeName,entityGuid,entityStatus,propagate,removePropagationsOnEntityDelete,validityPeriods,attributes,lastModifiedTS
```

### Glossary/term assignment

Common term-assignment fields:

```text
termGuid,displayText,relationGuid,description,expression,confidence,createdBy,status,steward
```

Exact fields depend on the glossary operation and API version.

### Lineage

Common lineage concepts to map:

```text
baseEntityGuid,lineageDirection,lineageDepth,lineageWidth,children,entities,relations,parentRelations,widthCounts
```

Use bounded depth/width and paging controls to prevent unexpectedly large responses.

### Unified Catalog data-column query (preview when used)

Request controls can include:

```text
filter,includingOrphans,includeAssetDetails,includeColumnDetails,skip,top
```

Possible response concepts include:

```text
id,source.type,source.assetId,source.columnId,assetDetails.assetId,assetDetails.name,assetDetails.fqn
```

Preview APIs require explicit opt-in, pinned API versions, and compatibility testing.

## 5. Microsoft Agent 365 fields to capture

Agent 365 package APIs differ by language and version. Keep SDK-specific models behind an adapter and map them into these stable categories.

### Agent/request context

```text
agentId,agentName,agentVersion,conversationId,activityId,channelId,tenantId,userId,locale,correlationId,operation,inputType,inputText,timestamp
```

### Runtime result

```text
status,outputType,outputText,toolCalls,notifications,artifacts,usage,durationMs,errorCode,retryable
```

### Tool call

```text
toolName,toolVersion,callId,arguments,startTime,endTime,durationMs,status,resultSummary,errorCode
```

Do not log complete tool arguments/results unless an allowlist confirms they contain no secrets or personal data.

### Notification

```text
notificationId,type,title,body,recipientId,recipientType,channel,priority,createdAt,expiresAt,status,correlationId,metadata
```

### Observability

```text
traceId,spanId,parentSpanId,serviceName,serviceVersion,operationName,startTime,endTime,durationMs,statusCode,statusMessage,attributes,events,links
```

Recommended safe attributes:

```text
agent.name,agent.version,adapter.name,operation.name,http.method,http.status_code,retry.count,result.count,tenant.hash,user.hash
```

Never record tokens, secrets, raw prompts containing sensitive data, notification bodies, or complete user identifiers as telemetry attributes by default.

## 6. Normalized script output

Map all adapters to a stable contract:

```json
{
  "source": "purview|entra|a365",
  "resourceType": "user|group|application|servicePrincipal|asset|classification|term|notification|trace",
  "id": "",
  "name": "",
  "qualifiedName": "",
  "description": "",
  "status": "",
  "tenantId": "",
  "owners": [],
  "members": [],
  "roles": [],
  "permissions": [],
  "classifications": [],
  "terms": [],
  "labels": [],
  "createdAt": null,
  "updatedAt": null,
  "sourceVersion": "",
  "correlationId": "",
  "raw": null
}
```

Only populate fields relevant to the resource. Prefer `null` or an empty array consistently and document that convention.

## 7. Field-selection checklist

Before adding a field to a script, answer:

- [ ] Which customer requirement uses this field?
- [ ] Which endpoint and API version returns it?
- [ ] Is it returned by default, or must it be explicitly selected/expanded?
- [ ] Which delegated/application permission is required?
- [ ] Does the caller also require an Entra or Purview role?
- [ ] Is the field personal, confidential, credential-related, or security-sensitive?
- [ ] Can it be omitted from logs and telemetry?
- [ ] How is `null`, missing, or permission-redacted data handled?
- [ ] Is paging, delta synchronization, or a continuation token required?
- [ ] Is the field stable or preview-only?
- [ ] Is it covered by mapping and redaction tests?

## 8. Copy/paste field sets

### Basic user inventory

```text
id,displayName,userPrincipalName,mail,accountEnabled,userType,jobTitle,department,companyName,officeLocation,createdDateTime
```

### Basic group inventory

```text
id,displayName,description,mail,mailEnabled,securityEnabled,groupTypes,visibility,createdDateTime,isAssignableToRole
```

### Basic application inventory

```text
id,appId,displayName,description,createdDateTime,signInAudience,publisherDomain,verifiedPublisher,identifierUris,tags
```

### Basic service-principal inventory

```text
id,appId,displayName,description,accountEnabled,servicePrincipalType,appOwnerOrganizationId,appRoleAssignmentRequired,servicePrincipalNames,tags,createdDateTime
```

### Basic Purview asset mapping

```text
guid,typeName,status,attributes.name,attributes.qualifiedName,attributes.description,collectionId,contacts,classifications,meanings,labels,createTime,updateTime,lastModifiedTS
```

### Basic Agent 365 telemetry

```text
agentId,agentName,agentVersion,conversationId,activityId,correlationId,operation,status,durationMs,errorCode,retryable
```

## 9. Official schema references

- Agent 365 SDK for .NET: https://learn.microsoft.com/en-us/dotnet/api/agent365-sdk-dotnet/agent365-overview
- Microsoft 365 Agents SDK: https://learn.microsoft.com/en-us/microsoft-365/agents-sdk/
- Purview Data Map REST reference: https://learn.microsoft.com/en-us/rest/api/purview/datamapdataplane/
- Purview entity get operation: https://learn.microsoft.com/en-us/rest/api/purview/datamapdataplane/entity/get
- Purview discovery query: https://learn.microsoft.com/en-us/rest/api/purview/datamapdataplane/discovery/query
- Microsoft Graph resource reference: https://learn.microsoft.com/en-us/graph/api/overview
- Graph user resource: https://learn.microsoft.com/en-us/graph/api/resources/user
- Graph group resource: https://learn.microsoft.com/en-us/graph/api/resources/group
- Graph application resource: https://learn.microsoft.com/en-us/graph/api/resources/application
- Graph service principal resource: https://learn.microsoft.com/en-us/graph/api/resources/serviceprincipal
- Graph app role assignment resource: https://learn.microsoft.com/en-us/graph/api/resources/approleassignment
