package com.devqa.devqaserver.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.util.Date;

@Data
@TableName(value = "qa_question_log")
public class QaQuestionLog {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String sessionId;
    private String question;
    private String answer;
    private String mode;
    private Boolean hitKnowledge;
    private String docIds;
    private String model;
    private Integer latencyMs;
    private Date createTime;

}
