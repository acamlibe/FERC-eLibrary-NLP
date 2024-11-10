using System;
using System.Collections.Generic;

namespace WebUI;

public partial class Summary
{
    public int SummaryId { get; set; }

    public string SummaryText { get; set; } = null!;

    public string ProjectId { get; set; } = null!;

    public string OriginalFileName { get; set; } = null!;

    public string FileText { get; set; } = null!;

    public byte[] FileBinary { get; set; } = null!;

    public string ExtractedFileName { get; set; } = null!;
}
