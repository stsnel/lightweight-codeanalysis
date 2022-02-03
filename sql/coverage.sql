; Query for retrieving logged line data
SELECT
  log_line.id as log_id,
  file.path as file,
  log_context.context as log_context,
  log_line.line_number as line_number
FROM
  log_line
  LEFT JOIN log_context ON log_context.id = log_line.log_context_id
  LEFT JOIN file ON log_line.file_id = file.id;

