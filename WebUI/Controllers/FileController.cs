using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace WebUI.Controllers;

[ApiController]
[Route("api/files")]
public class FileController (IDbContextFactory<FercSummaryContext> contextFactory) : ControllerBase
{
    [HttpGet("{summaryId}")]
    public async Task<IActionResult> Index([FromRoute] int summaryId)
    {
        await using var context = await contextFactory.CreateDbContextAsync();

        var file = await context.Summaries
            .Where(s => s.SummaryId == summaryId)
            .Select(s => new { s.FileBinary, s.OriginalFileName })
            .SingleOrDefaultAsync();

        if (file == null)
        {
            return NotFound();
        }

        string? extension = Path.GetExtension(file.OriginalFileName).ToLower();

        string mimeType = extension switch
        {
            ".pdf" => "application/pdf",
            _ => "application/octet-stream"
        };

        byte[] fileBytes = file.FileBinary;

        return File(fileBytes, mimeType);
    }
}