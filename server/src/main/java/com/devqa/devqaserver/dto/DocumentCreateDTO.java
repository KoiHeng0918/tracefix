package com.devqa.devqaserver.dto;


import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class DocumentCreateDTO {
    @NotBlank(message = "标题不可以为空")
    private String title;
    @NotBlank(message = "未填写分类")
    private String category;
    private String source;
    @NotBlank(message = "正文不可为空")
    private String content;

}
