package com.devqa.devqaserver;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.devqa.devqaserver.mapper")
public class DevqaServerApplication {

	public static void main(String[] args) {
		SpringApplication.run(DevqaServerApplication.class, args);
	}

}
