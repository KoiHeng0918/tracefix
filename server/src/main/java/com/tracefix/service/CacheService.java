package com.tracefix.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.time.Duration;

/**
 * P2 缓存骨架：诊断结果缓存、限流计数、幂等键都可以放这里。
 * 现在先提供最基础的方法，后续按真实需求接入。
 */
@Service
public class CacheService {

    @Autowired
    private StringRedisTemplate redisTemplate;

    public void put(String key, String value, Duration ttl) {
        redisTemplate.opsForValue().set(key, value, ttl);
    }

    public String get(String key) {
        return redisTemplate.opsForValue().get(key);
    }

    public boolean setIfAbsent(String key, String value, Duration ttl) {
        Boolean ok = redisTemplate.opsForValue().setIfAbsent(key, value, ttl);
        return Boolean.TRUE.equals(ok);
    }
}
