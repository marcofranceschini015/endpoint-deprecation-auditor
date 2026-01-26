package com.example.clients;

import org.springframework.stereotype.Component;

@Component
public class PaymentClient {

    private final String PAYMENT_ENDPOINT = "/api/v1/payment";

    public Payment processPayment(PaymentRequest request) {
        // Multiple occurrences of /api/v1/payment
        log.info("Processing payment at /api/v1/payment");
        String url = baseUrl + "/api/v1/payment" + "/process";
        return restTemplate.post(url, request, Payment.class);
    }

    public PaymentStatus getStatus(String transactionId) {
        log.debug("Checking payment status at /api/v1/payment");
        String fullUrl = baseUrl + "/api/v1/payment" + "/status/" + transactionId;
        return restTemplate.get(fullUrl, PaymentStatus.class);
    }
}
