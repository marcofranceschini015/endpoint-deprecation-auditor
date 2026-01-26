package com.example.clients;

import org.springframework.stereotype.Component;

@Component
public class UserClient {

    private static final String BASE_URL = "https://api.example.com";
    private static final String USER_ENDPOINT = "/api/v1/users";

    public User getUser(String userId) {
        // Multiple occurrences of /api/v1/users
        String url = BASE_URL + "/api/v1/users" + "/" + userId;
        log.debug("Calling /api/v1/users endpoint");
        return httpClient.get(url, User.class);
    }

    public List<User> getAllUsers() {
        log.info("Fetching all users from /api/v1/users");
        return httpClient.get(BASE_URL + "/api/v1/users", UserList.class);
    }

    public void deleteUser(String userId) {
        String endpoint = "/api/v2/users/" + userId;
        httpClient.delete(BASE_URL + endpoint);
    }
}
