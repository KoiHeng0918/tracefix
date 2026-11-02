package com.tracefix;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.tracefix.mapper")
public class TraceFixApplication {

	public static void main(String[] args) {
		SpringApplication.run(TraceFixApplication.class, args);
	}

}
