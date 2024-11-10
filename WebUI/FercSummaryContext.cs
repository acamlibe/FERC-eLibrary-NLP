using System;
using System.Collections.Generic;
using Microsoft.EntityFrameworkCore;

namespace WebUI;

public partial class FercSummaryContext : DbContext
{
    public FercSummaryContext()
    {
    }

    public FercSummaryContext(DbContextOptions<FercSummaryContext> options)
        : base(options)
    {
    }

    public virtual DbSet<Project> Projects { get; set; }

    public virtual DbSet<Summary> Summaries { get; set; }

    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        => optionsBuilder.UseNpgsql("Host=localhost;Port=5432;Database=fercsummary;Username=alic;Password=FercSummary!");

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Project>(entity =>
        {
            entity.HasKey(e => e.ProjectId).HasName("project_pkey");

            entity.ToTable("project");

            entity.Property(e => e.ProjectId).HasColumnName("project_id");
            entity.Property(e => e.CapacityKw).HasColumnName("capacity_kw");
            entity.Property(e => e.DamAnnualGeneration).HasColumnName("dam_annual_generation");
            entity.Property(e => e.DamBalancingAuthorityCode).HasColumnName("dam_balancing_authority_code");
            entity.Property(e => e.DamCapacityKw).HasColumnName("dam_capacity_kw");
            entity.Property(e => e.DamCoordinate).HasColumnName("dam_coordinate");
            entity.Property(e => e.DamCounty).HasColumnName("dam_county");
            entity.Property(e => e.DamEiaId).HasColumnName("dam_eia_id");
            entity.Property(e => e.DamElectricReliabilityCorporationRegion).HasColumnName("dam_electric_reliability_corporation_region");
            entity.Property(e => e.DamGenerators).HasColumnName("dam_generators");
            entity.Property(e => e.DamHuc).HasColumnName("dam_huc");
            entity.Property(e => e.DamHucFull).HasColumnName("dam_huc_full");
            entity.Property(e => e.DamLicenseExpiration).HasColumnName("dam_license_expiration");
            entity.Property(e => e.DamLicenseIssuance).HasColumnName("dam_license_issuance");
            entity.Property(e => e.DamMode).HasColumnName("dam_mode");
            entity.Property(e => e.DamName).HasColumnName("dam_name");
            entity.Property(e => e.DamOwner).HasColumnName("dam_owner");
            entity.Property(e => e.DamOwnershipType).HasColumnName("dam_ownership_type");
            entity.Property(e => e.DamPerformance).HasColumnName("dam_performance");
            entity.Property(e => e.DamPermittingAgency).HasColumnName("dam_permitting_agency");
            entity.Property(e => e.DamPumpedStorageAnnualGeneration).HasColumnName("dam_pumped_storage_annual_generation");
            entity.Property(e => e.DamPumpedStorageCapacityKw).HasColumnName("dam_pumped_storage_capacity_kw");
            entity.Property(e => e.DamPumpedStoragePerformance).HasColumnName("dam_pumped_storage_performance");
            entity.Property(e => e.DamRegionalEnergyDeploymentSystem).HasColumnName("dam_regional_energy_deployment_system");
            entity.Property(e => e.DamSector).HasColumnName("dam_sector");
            entity.Property(e => e.DamStartup).HasColumnName("dam_startup");
            entity.Property(e => e.DamState).HasColumnName("dam_state");
            entity.Property(e => e.DamTransmissionOwner).HasColumnName("dam_transmission_owner");
            entity.Property(e => e.DamType).HasColumnName("dam_type");
            entity.Property(e => e.DamWaterway).HasColumnName("dam_waterway");
            entity.Property(e => e.ExpirationDate).HasColumnName("expiration_date");
            entity.Property(e => e.ExtensionDeterminationDate).HasColumnName("extension_determination_date");
            entity.Property(e => e.ExtensionDeterminationMo).HasColumnName("extension_determination_mo");
            entity.Property(e => e.ExtensionRequestedDate).HasColumnName("extension_requested_date");
            entity.Property(e => e.ExtensionRequestedMo).HasColumnName("extension_requested_mo");
            entity.Property(e => e.FileDate).HasColumnName("file_date");
            entity.Property(e => e.IssueDate).HasColumnName("issue_date");
            entity.Property(e => e.LicenseProcessDurationYrs).HasColumnName("license_process_duration_yrs");
            entity.Property(e => e.LicenseProcessType).HasColumnName("license_process_type");
            entity.Property(e => e.NumberOfDams).HasColumnName("number_of_dams");
            entity.Property(e => e.Organization).HasColumnName("organization");
            entity.Property(e => e.PendingApplicationType).HasColumnName("pending_application_type");
            entity.Property(e => e.PreFileBranch).HasColumnName("pre_file_branch");
            entity.Property(e => e.PreFileDate).HasColumnName("pre_file_date");
            entity.Property(e => e.ProjectName).HasColumnName("project_name");
            entity.Property(e => e.SearchScore).HasColumnName("search_score");
            entity.Property(e => e.State).HasColumnName("state");
            entity.Property(e => e.Status).HasColumnName("status");
            entity.Property(e => e.TypeDescription).HasColumnName("type_description");
            entity.Property(e => e.Waterway).HasColumnName("waterway");
        });

        modelBuilder.Entity<Summary>(entity =>
        {
            entity.HasKey(e => e.SummaryId).HasName("summary_pkey");

            entity.ToTable("summary");

            entity.Property(e => e.SummaryId).HasColumnName("summary_id");
            entity.Property(e => e.ExtractedFileName).HasColumnName("extracted_file_name");
            entity.Property(e => e.FileBinary).HasColumnName("file_binary");
            entity.Property(e => e.FileText).HasColumnName("file_text");
            entity.Property(e => e.OriginalFileName).HasColumnName("original_file_name");
            entity.Property(e => e.ProjectId).HasColumnName("project_id");
            entity.Property(e => e.SummaryText).HasColumnName("summary_text");
        });

        OnModelCreatingPartial(modelBuilder);
    }

    partial void OnModelCreatingPartial(ModelBuilder modelBuilder);
}
