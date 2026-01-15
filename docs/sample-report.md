# Endpoint Deprecation Assessment Report

---

## Endpoint Information

- **Endpoint path:** `/v1/users/verify`
- **Controller file:** `service-a/src/main/java/com/example/UserController.java`
- **Handler method:** `verifyUser`

---

## Log Extraction

- **Extracted log template:**  
  `"Calling user verification endpoint"`

- **Log source:** Controller method

- **Fallback used:** No

---

## Runtime Usage (Graylog)

- **Time range analyzed:** Last 30 days
- **Query used:**  
  `"Calling user verification endpoint"`
- **Total occurrences:** **0**

---

## Code Usage Analysis

- **Number of matches:** **0**
- **Referencing files:**  
  _No references found_

---

## Automated Recommendation

✅ **Candidate for deprecation**

The endpoint shows:
- No runtime usage in the analyzed time range
- No references across the scanned codebases

It is safe to:
- Mark the endpoint as deprecated in documentation
- Schedule removal of related controller logic

---

## Warnings

_No warnings detected_

---

## Metadata

- **Analysis timestamp:** 2026-01-15T10:42:00Z
- **Report version:** v0.1
- **Runtime integrations enabled:** None
- **Static analysis only:** Yes
