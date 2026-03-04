@{
    Rules = @{
        PSAvoidUsingWriteHost = @{
            Enable = $false
        }
        PSAvoidUsingConvertToSecureStringWithPlainText = @{
            Enable = $true
        }
        PSUseApprovedVerbs = @{
            Enable = $true
        }
        PSUseDeclaredVarsMoreThanAssignments = @{
            Enable = $true
        }
    }
}
