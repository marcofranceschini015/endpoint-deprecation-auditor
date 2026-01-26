package com.example.clients;

import org.springframework.stereotype.Component;

@Component
public class OrderClient {

    public Order getOrder(String orderId) {
        String url = "/api/v1/orders/" + orderId;
        return httpClient.get(url, Order.class);
    }

    public List<Order> listOrders() {
        return httpClient.get("/api/v2/orders", OrderList.class);
    }
}
