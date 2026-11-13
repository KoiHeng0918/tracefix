package com.tracefix.common;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import lombok.Data;

import java.util.List;

/**
 * 分页返回结构：当前页数据 + 总条数 + 页码信息。
 * 只把前端需要的字段暴露出去，不直接返回 MyBatis-Plus 的 Page 对象。
 */
@Data
public class PageResult<T> {
    /** 当前页数据 */
    private List<T> records;

    /** 总条数 */
    private long total;

    /** 当前页码，从 1 开始 */
    private long pageNum;

    /** 每页条数 */
    private long pageSize;

    public static <T> PageResult<T> of(Page<T> page) {
        PageResult<T> result = new PageResult<>();
        result.setRecords(page.getRecords());
        result.setTotal(page.getTotal());
        result.setPageNum(page.getCurrent());
        result.setPageSize(page.getSize());
        return result;
    }
}
