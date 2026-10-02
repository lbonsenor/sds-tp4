package ar.edu.itba.sds.config;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class GridUtils {

    public static <T> List<List<T>> cartesianProduct(List<List<T>> lists) {
        if (lists == null || lists.isEmpty()) {
            return Collections.emptyList();
        }
        List<List<T>> result = new ArrayList<>();
        cartesianProductHelper(lists, 0, new ArrayList<>(), result);
        return result;
    }

    private static <T> void cartesianProductHelper(
            List<List<T>> lists, int depth, List<T> current, List<List<T>> result) {
        if (depth == lists.size()) {
            result.add(new ArrayList<>(current));
            return;
        }
        for (T item : lists.get(depth)) {
            current.add(item);
            cartesianProductHelper(lists, depth + 1, current, result);
            current.removeLast();
        }
    }
}
