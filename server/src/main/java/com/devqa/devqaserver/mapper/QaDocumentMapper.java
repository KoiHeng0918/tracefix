package com.devqa.devqaserver.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.devqa.devqaserver.entity.QaDocument;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface QaDocumentMapper extends BaseMapper<QaDocument> {
}
