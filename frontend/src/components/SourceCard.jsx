function SourceCard({ source }) {
  return (
    <div className="source-card">
      <div className="source-document">
        {source.document_name}
      </div>

      <div className="source-details">
        <span>Page {source.page_number}</span>
        <span>Score {source.score.toFixed(4)}</span>
      </div>
    </div>
  );
}

export default SourceCard;