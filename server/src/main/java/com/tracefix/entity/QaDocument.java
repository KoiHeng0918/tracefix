package com.tracefix.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.util.Date;

/**
 * 知识文档表（P1 原始资料）。
 * 对应表：qa_document
 */
@Data
@TableName(value = "qa_document")
public class QaDocument {
    /** 主键 */
    @TableId(type = IdType.AUTO)
    private Long id;

    /** 文档标题 */
    private String title;

    /** 分类，如 spring、redis、errors */
    private String category;

    /** 来源 */
    private String source;

    /** 文档原文 */
    private String content;

    /** 切分后的块数 */
    private Integer chunkCount;

    /** 处理状态：PENDING / PROCESSING / DONE / FAILED */
    private String status;

    /** 创建时间 */
    private Date createTime;

    /** 更新时间 */
    private Date updateTime;

}
