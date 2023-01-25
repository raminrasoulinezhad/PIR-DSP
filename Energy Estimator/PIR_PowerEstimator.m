function [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, functionality, index, N, kernel, stride, MAC)
     
    Pb = 205;
    Psr = 44;
    Prf = 40;
    Pc = 23;
    PRFe = 12.5;
    PSRe = 2;
    Pf = 1;
    RFs = 4;
    
    
    %%%%%%%%%%%%%%%%%%
    % To control Stream
    %Stream = 0;
    Stream = 1;
    %%%%%%%%%%%%%%%%%%
    % To control RF
    
    % Have RF
    %PRFe;
    
    % No RF
    PRFe = Pf;
    RFs = 1;
    
    %%%%%%%%%%%%%%%%%%
    % To control the MAC powers
    Depth = 0;
    parameter_apply_MAC_powers = 1;
    PMACs = [8/0.09, 4/0.09, 2/0.09];
    PMAC = PMACs(Depth+1) * parameter_apply_MAC_powers;    
    PDSP48E2MAC = (28.4/0.090) * parameter_apply_MAC_powers;
    
    precisions = [9,4,2];
    CSF_per_presicion = precisions(Depth+1)/9;
    %PDSP48E2MAC = PMAC;
    %%%%%%%%%%%%%%%%%%
    
    
    
    switch functionality
        case '3D' 
            if ((stride == 1) && (kernel == 3))
                Power_Rimp(1) = Power_Rimp(1) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf         + PDSP48E2MAC) * MAC;
                if (Stream)
                    Power_Ours(1) = Power_Ours(1) + (( Pb + 2*Pc ) / (RFs*kernel*kernel) + PSRe    +     Pb/(index*index) + PRFe       + PMAC) * MAC;
                else
                    Power_Ours(1) = Power_Ours(1) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf         + PMAC) * MAC;
                end
            elseif ((stride == 2) && (kernel == 3))
                Power_Rimp(1) = Power_Rimp(1) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf         + PDSP48E2MAC) * MAC;
                if (Stream)
                    Power_Ours(1) = Power_Ours(1) + ((Pb+Pc)/(RFs*2*2) + PSRe   +   (Pb/(index*index)) + PRFe       + PMAC) * MAC;
                else
                    Power_Ours(1) = Power_Ours(1) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf       + PMAC) * MAC;
                end
                
            elseif ((stride == 2) && (kernel == 5))
                Power_Rimp(1) = Power_Rimp(1) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf         + PDSP48E2MAC) * MAC;
                if (Stream)
                    Power_Ours(1) = Power_Ours(1) + ((Pb+2*Pc)/(RFs*3*3) + PSRe   +   (Pb/(index*index)) + PRFe       + PMAC) * MAC;
                else
                    Power_Ours(1) = Power_Ours(1) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf       + PMAC) * MAC;
                end
                
            elseif ((stride == 2) && (kernel == 7))
                Power_Rimp(1) = Power_Rimp(1) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf         + PDSP48E2MAC) * MAC;
                if (Stream)
                    Power_Ours(1) = Power_Ours(1) + ((Pb+6*Pc)/(RFs*4*4) + PSRe   +   (Pb/(index*index)) + PRFe       + PMAC) * MAC;
                else
                    Power_Ours(1) = Power_Ours(1) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf       + PMAC) * MAC;
                end
                
            else 
                disp ('$$$ PIR_PowerEstimator: Error $$')
            end
        case 'DW'
            if ((stride == 1) && (kernel == 3))
                Power_Rimp(2) = Power_Rimp(2) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf         + PDSP48E2MAC) * MAC;
                if (Stream)
                    Power_Ours(2) = Power_Ours(2) + (( Pb + 2*Pc ) / (kernel*kernel) + PSRe    +     PRFe + Pb/(index*index)       + PMAC) * MAC;
                else
                    Power_Ours(2) = Power_Ours(2) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf       + PMAC) * MAC;
                end
                
            elseif ((stride == 1) && (kernel == 5))
                Power_Rimp(2) = Power_Rimp(2) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf         + PDSP48E2MAC) * MAC;
                if (Stream)
                    Power_Ours(2) = Power_Ours(2) + (( Pb + 6*Pc ) / (kernel*kernel) + PSRe    +     PRFe + Pb/(index*index)       + PMAC) * MAC;
                else
                    Power_Ours(2) = Power_Ours(2) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf       + PMAC) * MAC;
                end
                
            elseif ((stride == 1) && (kernel == 7))
                Power_Rimp(2) = Power_Rimp(2) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf         + PDSP48E2MAC) * MAC;
                if (Stream)
                    Power_Ours(2) = Power_Ours(2) + (( Pb + 12*Pc ) / (kernel*kernel) + PSRe    +     PRFe + Pb/(index*index)       + PMAC) * MAC;
                else
                    Power_Ours(2) = Power_Ours(2) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf       + PMAC) * MAC;
                end
                
            elseif ((stride == 2) && (kernel == 3))
                Power_Rimp(2) = Power_Rimp(2) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf         + PDSP48E2MAC) * MAC;
                if (Stream)
                    Power_Ours(2) = Power_Ours(2) + ((Pb+Pc)/(2*2) + PSRe   +   (Pb/(index*index)) + PRFe       + PMAC) * MAC;
                else
                    Power_Ours(2) = Power_Ours(2) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf       + PMAC) * MAC;
                end
                
            elseif ((stride == 2) && (kernel == 5))
                Power_Rimp(2) = Power_Rimp(2) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf         + PDSP48E2MAC) * MAC;
                if (Stream)
                    Power_Ours(2) = Power_Ours(2) + ((Pb+2*Pc)/(3*3) + PSRe   +   (Pb/(index*index)) + PRFe        + PMAC) * MAC;
                else
                    Power_Ours(2) = Power_Ours(2) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf        + PMAC) * MAC;
                end
                
            elseif ((stride == 2) && (kernel == 7))
                Power_Rimp(2) = Power_Rimp(2) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf         + PDSP48E2MAC) * MAC;
                if (Stream)
                    Power_Ours(2) = Power_Ours(2) + ((Pb+6*Pc)/(4*4) + PSRe   +   (Pb/(index*index)) + PRFe        + PMAC) * MAC;
                else
                    Power_Ours(2) = Power_Ours(2) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf        + PMAC) * MAC;
                end
                
            else 
                disp ('$$$ PIR_PowerEstimator: Error $$')
            end
            
        case 'PW'
                Power_Rimp(3) = Power_Rimp(3) + (Pb/N + Psr + Pf      +     (Pb/(index*index)) + Pf         + PDSP48E2MAC) * MAC;
                if (Stream)
                    Power_Ours(3) = Power_Ours(3) + ((Pb/N + Pc)/RFs + PSRe      +     (Pb/(index*index)) + PRFe       + PMAC) * MAC;
                else
                    Power_Ours(3) = Power_Ours(3) + (Pb/N + Psr + Pf      +     (Pb/(index*index)) + Pf       + PMAC) * MAC;
                end
                
        case 'FC'
                Power_Rimp(4) = Power_Rimp(4) + ((Pb/(N)) + Pf + Pb + Pf         + PDSP48E2MAC) * MAC;
                if (Stream)
                    Power_Ours(4) = Power_Ours(4) + ((Pb/(N)) + PSRe + Pb + PRFe       + PMAC) * MAC;
                else
                    Power_Ours(4) = Power_Ours(4) + ((Pb/(N)) + Pf + Pb + Pf       + PMAC) * MAC;
                end
                
        otherwise 
            disp ('$$$ PIR_PowerEstimator: Error $$')
    end    
    
    
    

end

