package com.example.services;

import org.springframework.stereotype.Service;

// This file should NOT be found by the scanner (no "Client" in filename)
@Service
public class NotAService {

    public void doSomething() {
        String endpoint = "/api/v1/users";
        System.out.println("This should not be scanned: " + endpoint);
    }
}
