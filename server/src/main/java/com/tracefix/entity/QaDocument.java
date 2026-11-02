package com.tracefix.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.util.Date;

@Data
@TableName(value ="qa_document")
public class QaDocument {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String title;
    private String category;
    private String source;
    private String content;
    private Integer chunkCount;
    private String status;
    private Date createTime;
    private Date updateTime;

}
