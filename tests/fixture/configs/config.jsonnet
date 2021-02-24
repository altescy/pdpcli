local dropped_columns = ["name", "job"];

{
  colt: {
    typekey: "type"
  },
  reader: {
    type: "csv"
  },
  pipeline: {
    type: "pipeline",
    stages: {
      drop_columns: {
        type: "col_drop",
        columns: dropped_columns,
      },
      encode: {
        type: "one_hot_encode",
        columns: "sex",
      },
      tokenize: {
        type: "tokenize_text",
        columns: "content",
      },
      vectorize: {
        type: "tfidf_vectorize_token_lists",
        column: "content",
        max_features: 10,
      }
    }
  }
}
