package com.example.clients.nested;

import org.springframework.stereotype.Component;

@Component
public class ApiClient {

    public void callApi() {
        // Test nested directory scanning
        String endpoint = "/api/v1/users";
        httpClient.get(endpoint);
    }
}
