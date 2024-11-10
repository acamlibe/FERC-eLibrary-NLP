using System;
using System.Collections.Generic;

namespace WebUI;

public partial class Project
{
    public string? CapacityKw { get; set; }

    public string? ExpirationDate { get; set; }

    public string? ExtensionDeterminationMo { get; set; }

    public string? ExtensionDeterminationDate { get; set; }

    public string? ExtensionRequestedMo { get; set; }

    public string? ExtensionRequestedDate { get; set; }

    public string? FileDate { get; set; }

    public string ProjectId { get; set; } = null!;

    public string? IssueDate { get; set; }

    public string? LicenseProcessDurationYrs { get; set; }

    public string? LicenseProcessType { get; set; }

    public string? NumberOfDams { get; set; }

    public string? Organization { get; set; }

    public string? PendingApplicationType { get; set; }

    public string? PreFileBranch { get; set; }

    public string? PreFileDate { get; set; }

    public string ProjectName { get; set; } = null!;

    public string State { get; set; } = null!;

    public string Status { get; set; } = null!;

    public string? TypeDescription { get; set; }

    public string? Waterway { get; set; }

    public string? SearchScore { get; set; }

    public string? DamAnnualGeneration { get; set; }

    public string? DamBalancingAuthorityCode { get; set; }

    public string? DamCapacityKw { get; set; }

    public string? DamCoordinate { get; set; }

    public string? DamCounty { get; set; }

    public string? DamEiaId { get; set; }

    public string? DamElectricReliabilityCorporationRegion { get; set; }

    public string? DamGenerators { get; set; }

    public string? DamHuc { get; set; }

    public string? DamHucFull { get; set; }

    public string? DamLicenseExpiration { get; set; }

    public string? DamLicenseIssuance { get; set; }

    public string? DamMode { get; set; }

    public string? DamName { get; set; }

    public string? DamOwner { get; set; }

    public string? DamOwnershipType { get; set; }

    public string? DamPerformance { get; set; }

    public string? DamPermittingAgency { get; set; }

    public string? DamPumpedStorageAnnualGeneration { get; set; }

    public string? DamPumpedStorageCapacityKw { get; set; }

    public string? DamPumpedStoragePerformance { get; set; }

    public string? DamRegionalEnergyDeploymentSystem { get; set; }

    public string? DamSector { get; set; }

    public string? DamStartup { get; set; }

    public string? DamState { get; set; }

    public string? DamTransmissionOwner { get; set; }

    public string? DamType { get; set; }

    public string? DamWaterway { get; set; }
}
